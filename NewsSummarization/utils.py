import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from gtts import gTTS
import os

def fetch_news(company_name):
    """
    Fetch news articles related to the given company name.
    """
    query = company_name.replace(" ", "+")
    url = f"https://news.google.com/search?q={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    for item in soup.find_all("article")[:10]:  # Limit to 10 articles
        title = item.find("a", class_="DY5T1d").text
        link = "https://news.google.com" + item.find("a", class_="DY5T1d")["href"][1:]
        content = fetch_article_content(link)
        articles.append({
            "title": title,
            "link": link,
            "content": content
        })
    return articles

def fetch_article_content(url):
    """
    Fetch the content of a news article from its URL.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")
    content = " ".join([p.text for p in paragraphs])
    return content

def summarize_article(content, max_length=100):
    """
    Generate a summary of the article content.
    """
    return content[:max_length] + "..." if len(content) > max_length else content

def analyze_sentiment(content):
    """
    Perform sentiment analysis on the article content.
    """
    analysis = TextBlob(content)
    if analysis.sentiment.polarity > 0:
        return "Positive"
    elif analysis.sentiment.polarity < 0:
        return "Negative"
    else:
        return "Neutral"

def generate_hindi_tts(text):
    """
    Generate a Hindi TTS audio file from the given text.
    """
    tts = gTTS(text, lang="hi")
    tts_file = "summary.mp3"
    tts.save(tts_file)
    return tts_file
