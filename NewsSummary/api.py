from flask import Flask, request, jsonify
from utils import fetch_news, analyze_sentiment, text_to_speech, compare_sentiments

app = Flask(__name__)

@app.route('/fetch_news', methods=['POST'])
def fetch_news_api():
    data = request.json
    company = data.get("company", "")

    print(f"Received Request for News: {company}")  # Debugging log
    articles = fetch_news(company)

    if not articles:
        return jsonify({"message": "No articles found", "articles": []}), 200

    # Perform sentiment analysis & get topics
    sentiment_data, processed_articles = compare_sentiments(articles)

    # Generate coverage differences and topic overlaps
    coverage_differences, topic_overlap = generate_coverage_comparison(processed_articles)

    response = {
        "Company": company,
        "Articles": processed_articles,
        "Comparative Sentiment Score": {
            "Sentiment Distribution": sentiment_data,
            "Coverage Differences": coverage_differences,
            "Topic Overlap": topic_overlap
        },
        "Final Sentiment Analysis": generate_final_sentiment(sentiment_data),
        "Audio": "[Play Hindi Speech]"
    }

    return jsonify(response)

@app.route('/analyze_sentiment', methods=['POST'])
def analyze_sentiment_api():
    data = request.json
    articles = data.get("articles", [])

    for article in articles:
        article["sentiment"] = analyze_sentiment(article["summary"])

    return jsonify({"articles": articles})

@app.route('/tts', methods=['POST'])
def tts_api():
    data = request.json
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    audio_file = text_to_speech(text)

    return jsonify({"audio_file": audio_file})

if __name__ == "__main__":
    app.run(debug=True)

