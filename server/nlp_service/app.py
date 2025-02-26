from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import chromadb
import torch
from transformers import pipeline
import os
from text_processor import TextProcessor
from model_manager import ModelManager
import aiohttp
from bs4 import BeautifulSoup
from typing import List
from embeddings_manager import EmbeddingsManager

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize embeddings manager
embeddings_manager = EmbeddingsManager()

# Initialize ChromaDB with custom embeddings
chroma_client = chromadb.PersistentClient(path="./db")
collection = chroma_client.get_or_create_collection(
    name="url_content",
    embedding_function=embeddings_manager
)

# Initialize text processor and model manager
text_processor = TextProcessor()
model_manager = ModelManager()

# Define request/response models
class ContentRequest(BaseModel):
    content: str
    url: str = ""  # Make url optional with default empty string

class QuestionRequest(BaseModel):
    question: str

class ContentResponse(BaseModel):
    success: bool

class QuestionResponse(BaseModel):
    answer: str
    confidence: float

class URLRequest(BaseModel):
    urls: List[str]

@app.post("/process_content", response_model=ContentResponse)
async def process_content(request: ContentRequest):
    try:
        # Process and chunk the content
        chunks = text_processor.split_into_chunks(request.content)
        
        # Generate embeddings and store in ChromaDB
        collection.add(
            documents=chunks,
            ids=[f"{request.url}_chunk_{i}" for i in range(len(chunks))],
            metadatas=[{"url": request.url} for _ in chunks]
        )
        
        return {"success": True}
    except Exception as e:
        print(f"Error in process_content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/question", response_model=QuestionResponse)
async def answer_question(request: QuestionRequest):
    try:
        # Get more results initially and filter with higher threshold
        results = collection.query(
            query_texts=[request.question],
            n_results=8  # Increased from 5
        )
        
        contexts = []
        for doc, distance in zip(
            results['documents'][0],
            results['distances'][0]
        ):
            similarity = 1 - (distance / 2)
            # Increased similarity threshold for better relevance
            if similarity > 0.4:  # Increased from 0.3
                contexts.append({
                    'text': doc,
                    'score': similarity
                })
        
        if not contexts:
            return {
                "answer": "I couldn't find any relevant information to answer your question.",
                "confidence": 0.0
            }
        
        # Sort by similarity and take top 3 most relevant chunks
        contexts.sort(key=lambda x: x['score'], reverse=True)
        context = "\n\n".join(ctx['text'] for ctx in contexts[:1])  # reduced to 1 as we are using generation model
        
        qa_result = model_manager.get_answer(
            question=request.question,
            context=context
        )
        
        return model_manager.format_response(qa_result)
    except Exception as e:
        print(f"Error in answer_question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest")
async def ingest_urls(request: URLRequest):
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for url in request.urls:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Remove unwanted elements
                            for element in soup(['script', 'style', 'meta', 'noscript', 'header', 'footer', 'nav']):
                                element.decompose()
                            
                            # Extract and clean text content
                            text_content = []
                            for paragraph in soup.find_all(['p', 'article', 'section', 'div']):
                                text = paragraph.get_text(strip=True)
                                if text:
                                    # Clean the text: remove special characters but keep basic punctuation
                                    cleaned_text = ' '.join(text.split())
                                    text_content.append(cleaned_text)
                            
                            content = ' '.join(text_content)
                            
                            # Process the cleaned content
                            if content:
                                await process_content(ContentRequest(
                                    content=content,
                                    url=url
                                ))
                            
                except Exception as e:
                    print(f"Error processing {url}: {str(e)}")
                    continue
            
            return {"success": True, "message": "URLs processed successfully"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000) 