import requests
import os
from textblob import TextBlob
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from TTS.api import TTS  # Import Coqui TTS

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
        if len(articles) < 10:
            print(f"Warning: Only {len(articles)} articles found.")
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

# Generate comparative analysis based on sentiment and topics
def generate_comparative_analysis(articles):
    sentiment_distribution = {
        "Positive": 0,
        "Negative": 0,
        "Neutral": 0
    }
    
    for article in articles:
        sentiment_distribution[article["sentiment"]] += 1
    
    # Extract topics from all articles
    all_topics = [set(article["topics"]) for article in articles]
    
    # Calculate common topics (topics that appear in at least 2 articles)
    topic_counter = Counter()
    for topics in all_topics:
        topic_counter.update(topics)
    common_topics = [topic for topic, count in topic_counter.items() if count >= 2]
    
    # Calculate unique topics for each article
    unique_topics = {}
    for i, article in enumerate(articles):
        if len(all_topics) > 1:
            other_topics = set.union(*[topics for j, topics in enumerate(all_topics) if j != i])
        else:
            other_topics = set()
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
                "The first article highlights positive developments, boosting confidence in the company's growth, "
                "while the second article raises concerns about potential challenges."
            )
        elif article1["sentiment"] == "Negative" and article2["sentiment"] == "Positive":
            impact = (
                "The first article raises concerns about challenges, while the second article highlights positive developments, "
                "boosting confidence in the company's growth."
            )
        else:
            impact = "Both articles provide a balanced perspective on the company's current situation."
        
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

# Generate a detailed summary text that includes sentiment distribution, key insights, and final sentiment analysis.
def generate_detailed_summary(comparative_analysis, overall_sentiment):
    """
    Combine sentiment distribution, key insights, and final sentiment analysis
    into a single detailed summary text.
    """
    summary_lines = []
    
    # Sentiment Distribution
    summary_lines.append("Sentiment Distribution:")
    for sentiment, count in comparative_analysis.get("Sentiment Distribution", {}).items():
        summary_lines.append(f"{sentiment}: {count} articles.")
    
    # Key Insights from Comparative Analysis (e.g., coverage differences)
    summary_lines.append("\nKey Insights:")
    for idx, diff in enumerate(comparative_analysis.get("Coverage Differences", []), 1):
        summary_lines.append(f"Comparison {idx}: {diff.get('Comparison')}")
        summary_lines.append(f"Impact {idx}: {diff.get('Impact')}")
    
    # Final Sentiment Analysis
    summary_lines.append("\nFinal Sentiment Analysis:")
    summary_lines.append(overall_sentiment)
    
    # Combine all lines into one text block
    detailed_summary = "\n".join(summary_lines)
    return detailed_summary

# Generate Hindi text-to-speech audio dynamically using Coqui TTS.
def generate_audio_summary_coqui(comparative_analysis, overall_sentiment, company_name):
    """
    Creates a comprehensive audio summary that includes:
    - Sentiment Distribution: Count of positive, negative, and neutral articles.
    - Key Insights: Comparative analysis details such as coverage differences.
    - Final Sentiment Analysis: Overall sentiment conclusion.
    The summary is translated into Hindi and then converted to speech using Coqui TTS.
    """
    # Generate the detailed summary text
    detailed_summary = generate_detailed_summary(comparative_analysis, overall_sentiment)
    
    # Translate the summary into Hindi
    translated_summary = GoogleTranslator(source="auto", target="hi").translate(detailed_summary)
    
    # Initialize Coqui TTS with a Hindi-supported model.
    # Replace "tts_models/hi/vits" with the actual model identifier available from Coqui TTS if necessary.
    tts_model = TTS(model_name="tts_models/hi/vits", progress_bar=False, gpu=False)
    
    # Define the output audio file path (using .wav format for Coqui TTS)
    audio_filename = f"static/{company_name}_summary_audio.wav"
    
    # Generate the speech audio and save to file
    tts_model.tts_to_file(translated_summary, file_path=audio_filename)
    
    return f"http://127.0.0.1:8000/static/{company_name}_summary_audio.wav"
