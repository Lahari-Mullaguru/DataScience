from flask import Flask, request, jsonify, send_from_directory
from utils import (
    fetch_news, 
    compare_sentiments, 
    generate_coverage_comparison, 
    generate_final_sentiment, 
    text_to_speech
)
import os

app = Flask(__name__)

# Route to serve static files (Hindi TTS Audio)
@app.route('/static/<filename>')
def serve_audio(filename):
    return send_from_directory("static", filename)

@app.route('/fetch_news', methods=['POST'])
def fetch_news_api():
    data = request.json
    company = data.get("company", "").strip()

    if not company:
        return jsonify({"error": "Company name is required"}), 400

    try:
        # Fetch articles
        articles = fetch_news(company)

        # If no articles found, return early
        if not articles:
            return jsonify({
                "message": f"No articles found for {company}", 
                "Articles": []
            }), 200

        # Perform sentiment analysis
        sentiment_data, processed_articles = compare_sentiments(articles)

        # Compare coverage
        coverage_differences, topic_overlap = generate_coverage_comparison(processed_articles, company)

        # Generate consolidated summary (instead of only 2 articles)
        summary_text = " ".join([article["Summary"] for article in processed_articles])

        # Convert to Hindi Text-to-Speech (Handling Possible Errors)
        try:
            audio_link = text_to_speech(summary_text, company)
        except Exception as e:
            print(f"Text-to-Speech Error: {str(e)}")
            audio_link = None  # Fail gracefully if TTS doesn't work

        # Prepare Response
        response = {
            "Company": company,
            "Articles": processed_articles,
            "Comparative Sentiment Score": {
                "Sentiment Distribution": sentiment_data,
                "Coverage Differences": coverage_differences,
                "Topic Overlap": topic_overlap
            },
            "Final Sentiment Analysis": generate_final_sentiment(sentiment_data, company),
            "Audio": audio_link
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    # Ensure static directory exists
    if not os.path.exists("static"):
        os.makedirs("static")

    app.run(debug=True)
