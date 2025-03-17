import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from gtts import gTTS
import os

# Function to extract news articles
def fetch_news(company_name):
    search_url = f"https://news.google.com/rss/search?q={company_name}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.content, "lxml-xml")

    articles = []
    for item in soup.find_all("item")[:10]:  # Fetch top 10 articles
        title = item.title.text
        raw_summary = item.description.text
        summary = BeautifulSoup(raw_summary, "html.parser").get_text()  # Remove HTML tags
        url = item.link.text

        articles.append({
            "title": title,
            "summary": summary.strip(),  # Remove extra spaces
        })

    return articles

# Function for sentiment analysis
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    return "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"

# Function to extract topics from text
def extract_topics(summary):
    words = summary.split()  
    keywords = [word for word in words if len(word) > 3]  
    return list(set(keywords))[:5]  

# Function to compare sentiments
def compare_sentiments(articles):
    sentiment_count = {"Positive": 0, "Negative": 0, "Neutral": 0}

    for article in articles:
        sentiment = analyze_sentiment(article["summary"])
        topics = extract_topics(article["summary"])
        article["sentiment"] = sentiment
        article["topics"] = topics
        sentiment_count[sentiment] += 1

    return sentiment_count, articles

# Function to generate coverage differences
def generate_coverage_comparison(articles):
    coverage_differences = []
    topic_overlap = {
        "Common Topics": [],
        "Unique Topics in Article 1": [],
        "Unique Topics in Article 2": []
    }

    if len(articles) < 2:
        return coverage_differences, topic_overlap

    article1 = articles[0]
    article2 = articles[1]

    topics1 = article1["topics"]
    topics2 = article2["topics"]

    topic_overlap["Common Topics"] = list(set(topics1) & set(topics2))
    topic_overlap["Unique Topics in Article 1"] = list(set(topics1) - set(topics2))
    topic_overlap["Unique Topics in Article 2"] = list(set(topics2) - set(topics1))

    coverage_differences.append({
        "Comparison": f"Article 1 highlights {article1['title']}, while Article 2 discusses {article2['title']}.",
        "Impact": f"The first article emphasizes {topics1}, while the second article focuses on {topics2}."
    })

    return coverage_differences, topic_overlap

# Function to generate final sentiment statement
def generate_final_sentiment(sentiment_data):
    if sentiment_data["Positive"] > sentiment_data["Negative"]:
        return "The latest news coverage is mostly positive. Potential stock growth expected."
    elif sentiment_data["Negative"] > sentiment_data["Positive"]:
        return "The latest news coverage is mostly negative. Potential risks identified."
    else:
        return "The news coverage is balanced with mixed reactions."

# Function to convert text to speech
def text_to_speech(text):
    tts = gTTS(text, lang="hi")
    file_path = "static/output.mp3"
    tts.save(file_path)
    return file_path
