# NLP Service

This is a Natural Language Processing (NLP) service application.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

# Navigate to your project directory first, then:
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

## Installation

    pip install -r .\server\nlp_service\requirements.txt

## Run the application

# Frontend
    
    python -m http.server 3000

# Backend

    python server/nlp_service/app.py
