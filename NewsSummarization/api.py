from flask import Flask, request, jsonify
from utils import fetch_news, analyze_sentiment, text_to_speech, compare_sentiments, generate_coverage_comparison, generate_final_sentiment

app = Flask(__name__)

@app.route('/fetch_news', methods=['POST'])
def fetch_news_api():
    data = request.json
    company = data.get("company", "")

    articles = fetch_news(company)

    if not articles:
        return jsonify({"message": "No articles found", "articles": []}), 200

    sentiment_data, processed_articles = compare_sentiments(articles)
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

if __name__ == "__main__":
    app.run(debug=True)
