import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from gtts import gTTS
import os
import re
import unicodedata
from deep_translator import GoogleTranslator
import nltk

# Download stopwords for better topic extraction
nltk.download("stopwords")
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
        raw_summary = item.description.text
        summary = clean_text(BeautifulSoup(raw_summary, "html.parser").get_text())  

        if summary == title:  # Ensure summary isn't the same as title
            summary = f"{title} - More details inside."  

        articles.append({
            "Title": title,
            "Summary": summary
        })

    return articles

# Function to analyze sentiment dynamically for any text
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    return "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"

# Function to extract meaningful topics from article summaries
def extract_topics(summary):
    words = re.findall(r'\b[A-Za-z]{4,}\b', summary)  # Extract words of 4+ letters
    keywords = [word.lower() for word in words if word.lower() not in STOPWORDS]  # Remove stopwords
    return list(set(keywords))[:3]  # Return top 3 meaningful keywords

# Function to compare sentiments across multiple articles
def compare_sentiments(articles):
    sentiment_count = {"Positive": 0, "Negative": 0, "Neutral": 0}

    for article in articles:
        sentiment = analyze_sentiment(article["Summary"])
        topics = extract_topics(article["Summary"])
        article["Sentiment"] = sentiment
        article["Topics"] = topics

        sentiment_count[sentiment] += 1

    return sentiment_count, articles

# Function to generate coverage differences dynamically
def generate_coverage_comparison(articles, company_name):
    coverage_differences = []
    topic_overlap = {
        "Common Topics": [company_name],  # Ensure company name is always included
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
        common_topics.append("General Business News")  # Ensure at least one common topic

    topic_overlap["Common Topics"].extend(common_topics)
    topic_overlap["Unique Topics in Article 1"] = list(set(topics1) - set(topics2))
    topic_overlap["Unique Topics in Article 2"] = list(set(topics2) - set(topics1))

    coverage_differences.append({
        "Comparison": f"Article 1: {article1['Title']} vs. Article 2: {article2['Title']}.",
        "Impact": f"The first article emphasizes {' '.join(topics1)}, while the second article focuses on {' '.join(topics2)}."
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

    # 🔹 Ensure summary is translated into Hindi
    translated_text = GoogleTranslator(source="auto", target="hi").translate(text)
    
    hindi_intro = "यह हिंदी में अनुवादित समाचार है।"  
    full_text = hindi_intro + " " + translated_text  

    tts = gTTS(full_text, lang="hi", slow=False, tld="co.in")  
    tts.save(audio_filename)

    return f"http://127.0.0.1:5000/static/{company_name}_summary_audio.mp3"
