const API_URL = 'http://localhost:5000';
let processedUrls = [];

async function processURLs() {
    const urlInput = document.getElementById('urlInput');
    const urlStatus = document.getElementById('urlStatus');
    const questionInput = document.getElementById('questionInput');
    const askButton = document.getElementById('askButton');
    
    const urls = urlInput.value
        .split('\n')
        .map(url => url.trim())
        .filter(url => url !== '');
    
    if (urls.length === 0) {
        urlStatus.textContent = 'Please enter at least one URL';
        return;
    }
    
    urlStatus.textContent = 'Processing URLs...';
    
    try {
        const response = await fetch(`${API_URL}/api/ingest`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ urls }),
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Failed to process URLs');
        
        processedUrls = urls;
        urlStatus.textContent = 'URLs processed successfully!';
        questionInput.disabled = false;
        askButton.disabled = false;
    } catch (error) {
        console.error('Error:', error);
        urlStatus.textContent = `Error: ${error.message}`;
    }
}

async function askQuestion() {
    const questionInput = document.getElementById('questionInput');
    const questionStatus = document.getElementById('questionStatus');
    const answerBox = document.getElementById('answerBox');
    const confidenceScore = document.getElementById('confidenceScore');
    
    const question = questionInput.value.trim();
    if (!question) {
        questionStatus.textContent = 'Please enter a question';
        return;
    }
    
    questionStatus.textContent = 'Getting answer...';
    
    try {
        const response = await fetch(`${API_URL}/api/question`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ question }),
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Failed to get answer');
        
        answerBox.textContent = data.answer;
        confidenceScore.textContent = `Confidence: ${(data.confidence * 100).toFixed(2)}%`;
        questionStatus.textContent = '';
    } catch (error) {
        console.error('Error:', error);
        questionStatus.textContent = `Error: ${error.message}`;
    }
}
