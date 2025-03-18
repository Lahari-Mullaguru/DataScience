# api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict
import uvicorn

from utils import summarize_text, convert_text_to_speech, extract_topics, comparative_sentiment_analysis
from services.sentiment_service import sentiment_analyzer
from services.news_service import fetch_news  # Assume this accepts a company parameter and returns article dicts

app = FastAPI(title="News Summarization and TTS API")

class NewsArticleReport(BaseModel):
    title: str
    summary: str
    sentiment: str
    topics: List[str]
    published_at: datetime

class CompanyNewsReport(BaseModel):
    company: str
    articles: List[NewsArticleReport]
    comparative_sentiment: Dict[str, int]
    final_sentiment_analysis: str
    audio_file: str  # File path (or URL) to the generated Hindi TTS audio

@app.get("/news", response_model=List[NewsArticleReport])
def get_news(company: str):
    """
    Fetch news articles for the given company, process each article (summary, topics, sentiment)
    and return a list of structured reports.
    """
    articles = fetch_news(company)  # This function should fetch articles based on the company name.
    if not articles:
        raise HTTPException(status_code=404, detail="No news articles found.")

    processed_articles = []
    for article in articles:
        # Use content if available; otherwise fall back to description.
        content = article.get("content", "") or article.get("description", "")
        summary = summarize_text(content)
        topics = extract_topics(content)
        # Run sentiment analysis; sentiment_analyzer.analyze_sentiment should return a tuple (scores, label)
        sentiment_result = sentiment_analyzer.analyze_sentiment([content])[0]
        _, sentiment_label = sentiment_result
        processed_articles.append(NewsArticleReport(
            title=article["title"],
            summary=summary,
            sentiment=sentiment_label,
            topics=topics,
            published_at=datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
        ))
    
    return processed_articles

@app.get("/news/report", response_model=CompanyNewsReport)
def get_company_news_report(company: str):
    """
    Generate a comprehensive report for a given company including:
      - Summaries and sentiment analysis for each article
      - A comparative sentiment distribution
      - A final sentiment summary converted to Hindi speech (TTS output)
    """
    articles = fetch_news(company)
    if not articles:
        raise HTTPException(status_code=404, detail="No news articles found.")

    processed_articles = []
    # Process each article and store results for comparative analysis.
    for article in articles:
        content = article.get("content", "") or article.get("description", "")
        summary = summarize_text(content)
        topics = extract_topics(content)
        sentiment_result = sentiment_analyzer.analyze_sentiment([content])[0]
        _, sentiment_label = sentiment_result
        processed_articles.append({
            "title": article["title"],
            "summary": summary,
            "sentiment_label": sentiment_label,
            "topics": topics,
            "publishedAt": article["publishedAt"]
        })
    
    # Create a list of Pydantic models for the articles.
    article_reports = []
    for art in processed_articles:
        article_reports.append(NewsArticleReport(
            title=art["title"],
            summary=art["summary"],
            sentiment=art["sentiment_label"],
            topics=art["topics"],
            published_at=datetime.strptime(art["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
        ))
    
    # Perform comparative sentiment analysis
    comp_sentiment = comparative_sentiment_analysis(processed_articles)
    
    # Generate a simple final sentiment summary.
    if comp_sentiment["Positive"] >= comp_sentiment["Negative"]:
        final_analysis = "The overall news sentiment is positive."
    else:
        final_analysis = "The overall news sentiment is negative."
    
    # Convert the final sentiment analysis into Hindi speech.
    audio_file = convert_text_to_speech(final_analysis, lang="hi", filename=f"{company}_sentiment.mp3")
    
    report = CompanyNewsReport(
        company=company,
        articles=article_reports,
        comparative_sentiment=comp_sentiment,
        final_sentiment_analysis=final_analysis,
        audio_file=audio_file
    )
    return report

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
