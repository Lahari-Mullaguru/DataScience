from flask import Flask, request, jsonify, send_from_directory
from utils import fetch_news,analyze_sentiment,text_to_speech,compare_sentiments,generate_comparative_analysis
import os

app = Flask(__name__)

@app.route('/static/<filename>')
def serve_audio(filename):
    """Serves the generated Hindi audio file."""
    return send_from_directory("static", filename)

@app.route('/fetch_news', methods=['POST'])
def fetch_news_api():
    """Fetches news for a company and returns a structured JSON response."""
    data = request.json
    company = data.get("company", "").strip()

    if not company:
        return jsonify({"error": "Company name is required"}), 400

    articles = fetch_news(company)

    if not articles:
        return jsonify({"message": f"No articles found for {company}", "articles": []}), 200

    sentiment_data, processed_articles = compare_sentiments(articles)
    comparative_analysis = generate_comparative_analysis(processed_articles)

    # Generate Hindi TTS audio from the first two article summaries
    summary_text = " ".join([article["Summary"] for article in processed_articles[:2]])  
    audio_link = text_to_speech(summary_text, company)

    response = {
        "Company": company,
        "Articles": processed_articles,
        "Comparative Sentiment Score": {
            "Sentiment Distribution": sentiment_data,
            **comparative_analysis
        },
        "Final Sentiment Analysis": f"{company}’s latest news coverage is mostly {max(sentiment_data, key=sentiment_data.get)}. Potential stock growth expected.",
        "Audio": audio_link
    }

    return jsonify(response)

if __name__ == "__main__":
    if not os.path.exists("static"):
        os.makedirs("static")

    app.run(debug=True)
