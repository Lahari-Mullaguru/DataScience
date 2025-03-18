import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from gtts import gTTS
import os
import re
import unicodedata
import nltk
from newspaper import Article
from deep_translator import GoogleTranslator
from rake_nltk import Rake
from nltk.sentiment import SentimentIntensityAnalyzer
from gensim.summarization import summarize

nltk.download("vader_lexicon")
nltk.download("stopwords")
nltk.download("punkt")

sia = SentimentIntensityAnalyzer()
STOPWORDS = set(nltk.corpus.stopwords.words("english"))

# Function to clean text
def clean_text(text):
    text = unicodedata.normalize("NFKD", text).strip()
    return text.replace("\n", " ").replace("\r", " ")

# Fetch news from Google News RSS
def fetch_news(company_name):
    search_url = f"https://news.google.com/rss/search?q={company_name}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.content, "lxml-xml")

    articles = []
    for item in soup.find_all("item")[:10]:
        title = clean_text(item.title.text)
        url = item.link.text

        # Extract actual article summary
        article = Article(url)
        try:
            article.download()
            article.parse()
            article.nlp()
            summary = clean_text(article.summary)
        except:
            summary = "Summary not available. Click link for details."

        articles.append({
            "Title": title,
            "Summary": summary,
            "URL": url
        })

    return articles

# Sentiment analysis using VADER
def analyze_sentiment(text):
    scores = sia.polarity_scores(text)
    if scores["compound"] > 0.05:
        return "Positive"
    elif scores["compound"] < -0.05:
        return "Negative"
    else:
        return "Neutral"

# Extract topics using RAKE
def extract_topics(summary):
    rake = Rake()
    rake.extract_keywords_from_text(summary)
    return rake.get_ranked_phrases()[:3]  # Return top 3 ranked keywords

# Compare sentiments across articles
def compare_sentiments(articles):
    sentiment_count = {"Positive": 0, "Negative": 0, "Neutral": 0}

    for article in articles:
        sentiment = analyze_sentiment(article["Summary"])
        topics = extract_topics(article["Summary"])
        article["Sentiment"] = sentiment
        article["Topics"] = topics
        sentiment_count[sentiment] += 1

    return sentiment_count, articles

# Compare topic coverage
def generate_coverage_comparison(articles, company_name):
    if len(articles) < 2:
        return [], {"Common Topics": [company_name], "Unique Topics in Article 1": [], "Unique Topics in Article 2": []}

    article1, article2 = articles[:2]
    topics1, topics2 = set(article1["Topics"]), set(article2["Topics"])

    return [
        {
            "Comparison": f"Article 1: {article1['Title']} vs. Article 2: {article2['Title']}.",
            "Impact": f"Article 1 discusses {', '.join(topics1)}, while Article 2 focuses on {', '.join(topics2)}."
        }
    ], {
        "Common Topics": list(topics1 & topics2) or ["General Business News"],
        "Unique Topics in Article 1": list(topics1 - topics2),
        "Unique Topics in Article 2": list(topics2 - topics1)
    }

# Generate final sentiment statement
def generate_final_sentiment(sentiment_data, company_name):
    total_articles = sum(sentiment_data.values())
    if sentiment_data["Positive"] > sentiment_data["Negative"]:
        return f"{company_name}’s latest news coverage is mostly positive. Potential stock growth expected."
    elif sentiment_data["Negative"] > sentiment_data["Positive"]:
        return f"The latest news coverage about {company_name} is mostly negative. {round((sentiment_data['Negative'] / total_articles) * 100, 1)}% of articles indicate potential risks."
    else:
        return f"The news coverage for {company_name} is balanced with mixed reactions."

# Generate Hindi text-to-speech
def text_to_speech(text, company_name):
    audio_filename = f"static/{company_name}_summary_audio.mp3"
    translated_text = GoogleTranslator(source="auto", target="hi").translate(text)
    tts = gTTS(translated_text, lang="hi", slow=False, tld="co.in")
    tts.save(audio_filename)
    return f"http://127.0.0.1:5000/static/{company_name}_summary_audio.mp3"
