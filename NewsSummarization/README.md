# News Summarization and Sentiment Analysis Application

This application extracts news articles related to a given company, performs sentiment analysis, conducts a comparative analysis, and generates a Hindi text-to-speech summary.

## Features

- **News Extraction**: Fetches news articles using the NewsAPI.
- **Sentiment Analysis**: Analyzes sentiment (positive, negative, neutral) using TextBlob.
- **Comparative Analysis**: Compares sentiment and topics across multiple articles.
- **Text-to-Speech**: Converts the summary into Hindi speech using gTTS.
- **Web Interface**: Provides a simple web-based interface using Streamlit.

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Lahari-Mullaguru/DataScience.git
   cd DataScience/NewsSummarization
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
4. **Set up environment variables**:
   Create a .env file in the root directory.
   Add your NewsAPI key:
   ```bash
   NEWSAPI_API_KEY=your_api_key_here
6. **Run the FastAPI backend**:
   ```bash
   python -m uvicorn api:app --reload
8. **Run the Streamlit frontend**:
   ```bash
   streamlit run app.py
10. **Access the application**:
   Open your browser and go to http://localhost:8501.
   Enter a company name and click "Analyze News"
