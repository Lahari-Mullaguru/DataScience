@app.route('/fetch_news', methods=['POST'])
def fetch_news_api():
    data = request.json
    company = data.get("company", "")

    articles = fetch_news(company)

    if not articles:
        return jsonify({"message": f"No articles found for {company}", "articles": []}), 200

    sentiment_data, processed_articles = compare_sentiments(articles)

    coverage_differences, topic_overlap = generate_coverage_comparison(processed_articles, company)

    summary_text = " ".join([article["summary"] for article in processed_articles[:2]])  
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
        "Audio": audio_link  # Audio link at the end
    }

    return jsonify(response)
