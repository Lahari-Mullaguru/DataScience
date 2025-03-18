import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from gtts import gTTS
import os
import re

# Function to extract news articles dynamically for any company
def fetch_news(company_name):
    search_url = f"https://news.google.com/rss/search?q={company_name}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.content, "lxml-xml")

    articles = []
    for item in soup.find_all("item")[:10]:  # Fetch top 10 articles
        title = item.title.text.strip()
        raw_summary = item.description.text
        summary = BeautifulSoup(raw_summary, "html.parser").get_text().strip()  # Remove HTML tags
        url = item.link.text.strip()

        articles.append({
            "title": title,
            "summary": summary
        })

    return articles

# Function for sentiment analysis (dynamic for any text)
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    return "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"

# Function to extract meaningful topics (Dynamic)
def extract_topics(summary):
    words = re.findall(r'\b[A-Za-z]{4,}\b', summary)  # Extract words with length >= 4
    return list(set(words))[:3]  # Return top 3 keywords

# Function to compare sentiments dynamically for any company
def compare_sentiments(articles):
    sentiment_count = {"Positive": 0, "Negative": 0, "Neutral": 0}

    for article in articles:
        sentiment = analyze_sentiment(article["summary"])
        topics = extract_topics(article["summary"])
        article["sentiment"] = sentiment
        article["topics"] = topics
        sentiment_count[sentiment] += 1

    return sentiment_count, articles

# Function to generate coverage differences dynamically
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

# Function to generate final sentiment statement dynamically
def generate_final_sentiment(sentiment_data, company_name):
    if sentiment_data["Positive"] > sentiment_data["Negative"]:
        return f"{company_name}’s latest news coverage is mostly positive. Potential stock growth expected."
    elif sentiment_data["Negative"] > sentiment_data["Positive"]:
        return f"The latest news coverage about {company_name} is mostly negative. Potential risks identified."
    else:
        return f"The news coverage for {company_name} is balanced with mixed reactions."

# Function to convert text to speech dynamically
def text_to_speech(text, company_name):
    audio_filename = f"static/{company_name}_summary_audio.mp3"
    tts = gTTS(text, lang="hi")
    tts.save(audio_filename)

    # Return the direct link to the generated audio file
    return f"http://127.0.0.1:5000/{audio_filename}"
