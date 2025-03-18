from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils import fetch_news, summarize_article, analyze_sentiment, generate_hindi_tts
import os

app = FastAPI()

class CompanyRequest(BaseModel):
    company_name: str

@app.post("/fetch-news")
def fetch_news_endpoint(request: CompanyRequest):
    company_name = request.company_name
    articles = fetch_news(company_name)
    if not articles:
        raise HTTPException(status_code=404, detail="No articles found.")
    return {"articles": articles}

@app.post("/analyze-sentiment")
def analyze_sentiment_endpoint(request: CompanyRequest):
    company_name = request.company_name
    articles = fetch_news(company_name)
    if not articles:
        raise HTTPException(status_code=404, detail="No articles found.")
    
    sentiment_results = []
    for article in articles:
        sentiment = analyze_sentiment(article['content'])
        sentiment_results.append({
            "title": article['title'],
            "sentiment": sentiment
        })
    return {"sentiment_results": sentiment_results}

@app.post("/generate-tts")
def generate_tts_endpoint(request: CompanyRequest):
    company_name = request.company_name
    articles = fetch_news(company_name)
    if not articles:
        raise HTTPException(status_code=404, detail="No articles found.")
    
    positive_count = sum(1 for article in articles if analyze_sentiment(article['content']) == "Positive")
    negative_count = sum(1 for article in articles if analyze_sentiment(article['content']) == "Negative")
    neutral_count = sum(1 for article in articles if analyze_sentiment(article['content']) == "Neutral")
    
    summary_text = f"{company_name} के बारे में {len(articles)} लेख मिले। {positive_count} लेख सकारात्मक, {negative_count} लेख नकारात्मक, और {neutral_count} लेख तटस्थ हैं।"
    tts_file = generate_hindi_tts(summary_text)
    
    return {"tts_file": tts_file}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
