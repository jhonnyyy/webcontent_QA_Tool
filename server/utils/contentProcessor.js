// Function to split text into chunks
const splitIntoChunks = (text, chunkSize = 500) => {
  const words = text.split(' ');
  const chunks = [];
  let currentChunk = [];
  let currentLength = 0;

  for (const word of words) {
    if (currentLength + word.length > chunkSize && currentChunk.length > 0) {
      chunks.push(currentChunk.join(' '));
      currentChunk = [];
      currentLength = 0;
    }
    currentChunk.push(word);
    currentLength += word.length + 1; // +1 for space
  }

  if (currentChunk.length > 0) {
    chunks.push(currentChunk.join(' '));
  }

  return chunks;
};

// Function to find relevant context from ChromaDB
const findRelevantContext = async (collection, question, numResults = 3) => {
  try {
    const results = await collection.query({
      queryTexts: [question],
      nResults: numResults,
    });

    // Combine the most relevant chunks into a single context
    return results.documents[0].join('\n\n');
  } catch (error) {
    console.error('Error querying vector database:', error);
    throw error;
  }
};

// Original processContent function (now unused but kept for reference)
const processContent = async (question, content) => {
  // This is a placeholder for actual NLP/ML processing
  // In a real implementation, you would use a language model or similar
  
  // For demo purposes, just return a simple response
  return `Based on the provided content, here is a relevant answer to "${question}". 
          This is a placeholder response - in a real implementation, 
          this would use NLP/ML to generate an accurate answer from the content.`;
};

module.exports = {
  processContent,
  splitIntoChunks,
  findRelevantContext
}; 