from fastapi import FastAPI
from utils import fetch_news, analyze_sentiment, generate_comparative_analysis, text_to_speech_hindi

app = FastAPI()

@app.get("/analyze-news")
def analyze_news(company_name: str):
    # Fetch news articles
    articles = fetch_news(company_name)
    
    if not articles:
        return {"error": "No articles found for the given company."}
    
    # Perform sentiment analysis
    articles_with_sentiment = analyze_sentiment(articles)
    
    # Generate comparative analysis
    comparative_analysis = generate_comparative_analysis(articles_with_sentiment)
    
    # Generate Hindi TTS (optional, can be excluded if not needed in the API response)
    tts_output = text_to_speech_hindi(comparative_analysis)
    
    # Prepare the final output
    output = {
        "Company": company_name,
        "Articles": [
            {
                "Title": article["title"],
                "Summary": article["summary"],
                "Sentiment": article["sentiment"],
                "Topics": article["topics"]
            } for article in articles_with_sentiment
        ],
        "Comparative Sentiment Score": {
            "Sentiment Distribution": comparative_analysis["Sentiment Distribution"],
            "Coverage Differences": comparative_analysis["Coverage Differences"],
            "Topic Overlap": comparative_analysis["Topic Overlap"]
        },
        "Final Sentiment Analysis": f"{company_name}'s latest news coverage is mostly {max(comparative_analysis['Sentiment Distribution'], key=comparative_analysis['Sentiment Distribution'].get)}.",
        "Audio": tts_output  # Optional: Include the path to the TTS file
    }
    
    return output
