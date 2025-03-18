import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from gtts import gTTS
import os
import re
import unicodedata
from deep_translator import GoogleTranslator
import nltk
from newspaper import Article
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter

# Download necessary resources
nltk.download("stopwords")
nltk.download("punkt")
from nltk.corpus import stopwords
STOPWORDS = set(stopwords.words("english"))

# Function to clean text and remove unwanted Unicode characters
def clean_text(text):
    text = unicodedata.normalize("NFKD", text).strip()
    return text.replace("\n", " ").replace("\r", " ")  # Remove newlines

# Function to fetch news articles for any company dynamically
def fetch_news(company_name):
    search_url = f"https://news.google.com/rss/search?q={company_name}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.content, "lxml-xml")

    articles = []
    for item in soup.find_all("item")[:10]:  
        title = clean_text(item.title.text)
        article_url = item.link.text
        
        # Try fetching full article text
        summary = extract_article_summary(article_url)
        
        if not summary:
            summary = f"{title} - More details inside."  # Default fallback

        articles.append({
            "Title": title,
            "Summary": summary,
            "URL": article_url
        })
    return articles

# Function to fetch full article summary
def extract_article_summary(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()
        return article.summary
    except Exception as e:
        return None

# Function to analyze sentiment dynamically for any text
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    return "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"

# Function to extract meaningful topics using TF-IDF
def extract_topics(articles):
    vectorizer = TfidfVectorizer(stop_words='english', max_features=10)
    summaries = [article["Summary"] for article in articles]
    
    tfidf_matrix = vectorizer.fit_transform(summaries)
    feature_names = vectorizer.get_feature_names_out()
    top_keywords = Counter(feature_names).most_common(3)
    return [keyword[0] for keyword in top_keywords]

# Function to compare sentiments across multiple articles
def compare_sentiments(articles):
    sentiment_count = {"Positive": 0, "Negative": 0, "Neutral": 0}

    for article in articles:
        sentiment = analyze_sentiment(article["Summary"])
        topics = extract_topics([article])
        article["Sentiment"] = sentiment
        article["Topics"] = topics

        sentiment_count[sentiment] += 1

    return sentiment_count, articles

# Function to generate coverage differences dynamically
def generate_coverage_comparison(articles, company_name):
    coverage_differences = []
    topic_overlap = {
        "Common Topics": [company_name],  
        "Unique Topics in Article 1": [],
        "Unique Topics in Article 2": []
    }

    if len(articles) < 2:
        return coverage_differences, topic_overlap

    article1 = articles[0]
    article2 = articles[1]

    topics1 = article1["Topics"]
    topics2 = article2["Topics"]

    common_topics = list(set(topics1) & set(topics2))
    if not common_topics:
        common_topics.append("General Business News")

    topic_overlap["Common Topics"].extend(common_topics)
    topic_overlap["Unique Topics in Article 1"] = list(set(topics1) - set(topics2))
    topic_overlap["Unique Topics in Article 2"] = list(set(topics2) - set(topics1))

    coverage_differences.append({
        "Comparison": f"Article 1: {article1['Title']} vs. Article 2: {article2['Title']}.",
        "Impact": f"The first article focuses on {', '.join(topics1)}, while the second article highlights {', '.join(topics2)}."
    })

    return coverage_differences, topic_overlap

# Function to generate final sentiment analysis statement
def generate_final_sentiment(sentiment_data, company_name):
    total_articles = sum(sentiment_data.values())

    if sentiment_data["Positive"] > sentiment_data["Negative"]:
        return f"{company_name}’s latest news coverage is mostly positive. Potential stock growth expected."
    elif sentiment_data["Negative"] > sentiment_data["Positive"]:
        return f"The latest news coverage about {company_name} is mostly negative. {round((sentiment_data['Negative'] / total_articles) * 100, 1)}% of articles indicate potential risks."
    else:
        return f"The news coverage for {company_name} is balanced with mixed reactions."

# Function to generate Hindi text-to-speech audio dynamically
def text_to_speech(text, company_name):
    audio_filename = f"static/{company_name}_summary_audio.mp3"
    translated_text = GoogleTranslator(source="auto", target="hi").translate(text)
    
    tts = gTTS(translated_text, lang="hi", slow=False, tld="co.in")  
    tts.save(audio_filename)

    return f"http://127.0.0.1:5000/static/{company_name}_summary_audio.mp3"
