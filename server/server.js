const express = require('express');
const cors = require('cors');
const axios = require('axios');
const cheerio = require('cheerio');

const app = express();
app.use(cors());
app.use(express.json());

const NLP_SERVICE_URL = 'http://localhost:5000';

app.post('/api/ingest', async (req, res) => {
  const { urls } = req.body;
  
  try {
    for (const url of urls) {
      const response = await axios.get(url);
      const $ = cheerio.load(response.data);
      
      // Remove unwanted elements
      $('script, style, meta, noscript, header, footer, nav').remove();
      
      // Extract text content more carefully
      const content = $('body')
        .find('p, article, section, div')
        .map((_, element) => $(element).text().trim())
        .get()
        .filter(text => text.length > 0)
        .join(' ')
        .replace(/[\r\n]+/g, ' ')  // Replace newlines with spaces
        .replace(/\s+/g, ' ')      // Normalize spaces
        .trim();
      
      // Send content to Python NLP service
      await axios.post(`${NLP_SERVICE_URL}/process_content`, {
        content,
        url
      });
    }
    
    res.json({ success: true });
  } catch (error) {
    console.error('Error ingesting URLs:', error);
    res.status(500).json({ error: 'Failed to process URLs' });
  }
});

app.post('/api/question', async (req, res) => {
  const { question } = req.body;
  
  try {
    const response = await axios.post(`${NLP_SERVICE_URL}/api/question`, {
      question
    });
    
    res.json(response.data);  // Return the complete response
  } catch (error) {
    console.error('Error processing question:', error);
    res.status(500).json({ error: 'Failed to process question' });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
}); 