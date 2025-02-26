from typing import List
import nltk
from nltk.tokenize import sent_tokenize
import re

class TextProcessor:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')

    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        try:
            # Basic cleaning without complex regex
            # Remove extra whitespace
            text = ' '.join(text.split())
            
            # Basic punctuation cleanup
            text = text.replace('\n', ' ')
            text = text.replace('\r', ' ')
            text = text.replace('\t', ' ')
            
            # Remove multiple spaces
            text = ' '.join(word for word in text.split(' ') if word)
            
            return text.strip()
        except Exception as e:
            print(f"Error in clean_text: {str(e)}")
            return text

    def split_into_chunks(self, text: str, max_tokens: int = 500) -> List[str]:
        """Split text into chunks based on paragraphs and sentence boundaries."""
        try:
            # Clean the text first
            text = self.clean_text(text)
            
            # Split into paragraphs (split by double newlines or multiple spaces)
            paragraphs = [p.strip() for p in re.split(r'\n\s*\n|\s{2,}', text) if p.strip()]
            
            chunks = []
            current_chunk = []
            current_length = 0
            
            for paragraph in paragraphs:
                # Split paragraph into sentences
                sentences = sent_tokenize(paragraph)
                
                # Process each sentence in the paragraph
                for sentence in sentences:
                    sentence_length = len(sentence.split())  # Approximate token count
                    
                    # If single sentence exceeds max tokens, split it further
                    if sentence_length > max_tokens:
                        if current_chunk:
                            chunks.append(' '.join(current_chunk))
                            current_chunk = []
                            current_length = 0
                        
                        # Split long sentence into smaller parts while preserving words
                        words = sentence.split()
                        temp_chunk = []
                        temp_length = 0
                        
                        for word in words:
                            if temp_length + 1 > max_tokens:
                                chunks.append(' '.join(temp_chunk))
                                temp_chunk = [word]
                                temp_length = 1
                            else:
                                temp_chunk.append(word)
                                temp_length += 1
                        
                        if temp_chunk:
                            current_chunk = temp_chunk
                            current_length = temp_length
                    
                    # Normal sentence processing
                    elif current_length + sentence_length > max_tokens:
                        # Add current chunk to chunks
                        chunks.append(' '.join(current_chunk))
                        # Start new chunk with current sentence
                        current_chunk = [sentence]
                        current_length = sentence_length
                    else:
                        current_chunk.append(sentence)
                        current_length += sentence_length
                
                # Add paragraph boundary if we're continuing with the same chunk
                if current_chunk and paragraphs.index(paragraph) < len(paragraphs) - 1:
                    current_chunk.append("\n\n")
            
            # Add the last chunk if it exists
            if current_chunk:
                chunks.append(' '.join(current_chunk).replace("\n\n ", "\n\n"))
            
            # Clean up the chunks
            cleaned_chunks = []
            for chunk in chunks:
                # Remove extra spaces and newlines
                cleaned = re.sub(r'\s+', ' ', chunk)
                cleaned = cleaned.strip()
                if cleaned:
                    cleaned_chunks.append(cleaned)
            
            return cleaned_chunks
            
        except Exception as e:
            print(f"Error in split_into_chunks: {str(e)}")
            return [text]

    def extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # This is a placeholder for keyword extraction
        # You could implement various methods here:
        # - TF-IDF
        # - TextRank
        # - YAKE
        # - KeyBERT
        pass 