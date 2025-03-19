import requests
import os
from textblob import TextBlob
from gtts import gTTS
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key
API_KEY = os.getenv("NEWSAPI_API_KEY")
if not API_KEY:
    raise ValueError("API key not found. Please set the NEWSAPI_API_KEY environment variable.")

# Download NLTK data (only once)
nltk.download("punkt")
nltk.download("stopwords")

# Fetch news articles using NewsAPI
def fetch_news(company_name):
    API_ENDPOINT = "https://newsapi.org/v2/everything"
    
    params = {
        "q": company_name,
        "apiKey": API_KEY,
        "pageSize": 10,  # Fetch 10 articles
        "language": "en"
    }
    
    response = requests.get(API_ENDPOINT, params=params)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return [{
            "title": article["title"],
            "summary": article["description"],
            "content": article["content"]
        } for article in articles]
    else:
        print(f"Error: {response.status_code} - {response.text}")  # Debug statement
        return []

# Perform sentiment analysis using TextBlob
def analyze_sentiment(articles):
    for article in articles:
        blob = TextBlob(article["content"])
        sentiment_score = blob.sentiment.polarity
        if sentiment_score > 0:
            article["sentiment"] = "Positive"
        elif sentiment_score < 0:
            article["sentiment"] = "Negative"
        else:
            article["sentiment"] = "Neutral"
        
        # Extract topics dynamically
        article["topics"] = extract_topics(article["content"])
    return articles

# Extract topics from content
def extract_topics(content):
    if not content:
        return []
    
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(content.lower())
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    
    # Count word frequency and extract top 3 topics
    word_freq = Counter(filtered_words)
    topics = [word for word, _ in word_freq.most_common(3)]
    return topics

# Generate comparative analysis
def generate_comparative_analysis(articles):
    sentiment_distribution = {
        "Positive": 0,
        "Negative": 0,
        "Neutral": 0
    }
    
    for article in articles:
        sentiment_distribution[article["sentiment"]] += 1
    
    # Extract common and unique topics
    all_topics = [set(article["topics"]) for article in articles]
    common_topics = list(set.intersection(*all_topics))
    
    # Calculate unique topics for each article
    unique_topics = {}
    for i, article in enumerate(articles):
        other_topics = set.union(*[topics for j, topics in enumerate(all_topics) if j != i])
        unique_topics[f"Unique Topics in Article {i+1}"] = list(set(article["topics"]) - other_topics)
    
    # Dynamically generate coverage differences
    coverage_differences = []
    for i in range(len(articles) - 1):
        article1 = articles[i]
        article2 = articles[i + 1]
        
        # Generate comparison based on topics and sentiment
        comparison = (
            f"Article {i+1} discusses {', '.join(article1['topics'])} with a {article1['sentiment'].lower()} sentiment, "
            f"while Article {i+2} discusses {', '.join(article2['topics'])} with a {article2['sentiment'].lower()} sentiment."
        )
        
        # Generate impact based on sentiment
        if article1["sentiment"] == "Positive" and article2["sentiment"] == "Negative":
            impact = (
                f"The first article highlights positive developments, boosting confidence in the company's growth, "
                f"while the second article raises concerns about potential challenges."
            )
        elif article1["sentiment"] == "Negative" and article2["sentiment"] == "Positive":
            impact = (
                f"The first article raises concerns about challenges, while the second article highlights positive developments, "
                f"boosting confidence in the company's growth."
            )
        else:
            impact = (
                f"Both articles provide a balanced perspective on the company's current situation."
            )
        
        coverage_differences.append({
            "Comparison": comparison,
            "Impact": impact
        })
    
    comparative_analysis = {
        "Sentiment Distribution": sentiment_distribution,
        "Coverage Differences": coverage_differences,
        "Topic Overlap": {
            "Common Topics": common_topics,
            **unique_topics  # Add unique topics for each article
        }
    }
    
    return comparative_analysis

# Function to generate Hindi text-to-speech audio dynamically
def text_to_speech(text, company_name):
    audio_filename = f"static/{company_name}_summary_audio.mp3"

    # Ensure summary is translated into Hindi
    translated_text = GoogleTranslator(source="auto", target="hi").translate(text)
    
    hindi_intro = "यह हिंदी में अनुवादित समाचार है।"  
    full_text = hindi_intro + " " + translated_text  

    tts = gTTS(full_text, lang="hi", slow=False, tld="co.in")  
    tts.save(audio_filename)

    return audio_filename
