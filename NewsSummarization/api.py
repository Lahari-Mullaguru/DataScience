from flask import Flask, request, jsonify, send_from_directory
from utils import fetch_news, analyze_sentiment, text_to_speech, compare_sentiments, generate_coverage_comparison, generate_final_sentiment
import os

app = Flask(__name__)

# Serve the audio file for playback dynamically
@app.route('/static/<filename>')
def serve_audio(filename):
    return send_from_directory("static", filename)

@app.route('/fetch_news', methods=['POST'])
def fetch_news_api():
    data = request.json
    company = data.get("company", "")

    articles = fetch_news(company)

    if not articles:
        return jsonify({"message": f"No articles found for {company}", "articles": []}), 200

    sentiment_data, processed_articles = compare_sentiments(articles)
    coverage_differences, topic_overlap = generate_coverage_comparison(processed_articles)

    summary_text = " ".join([article["summary"] for article in processed_articles[:2]])  # Use top 2 articles
    audio_link = text_to_speech(summary_text, company)

    response = {
        "Company": company,
        "Articles": processed_articles,
        "Comparative Sentiment Score": {
            "Sentiment Distribution": sentiment_data,
            "Coverage Differences": coverage_differences,
            "Topic Overlap": topic_overlap
        },
        "Final Sentiment Analysis": generate_final_sentiment(sentiment_data, company),
        "Audio": audio_link  # Playable link to the audio summary
    }

    return jsonify(response)

if __name__ == "__main__":
    if not os.path.exists("static"):
        os.makedirs("static")
    app.run(debug=True)
