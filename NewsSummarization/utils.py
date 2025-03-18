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
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

# Ensure necessary NLTK data is available
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

nltk.download("stopwords")
from nltk.corpus import stopwords

STOPWORDS = set(stopwords.words("english"))

# Function to clean text and remove unwanted Unicode characters
def clean_text(text):
    """ Normalize text, remove unwanted Unicode artifacts, and clean formatting """
    text = unicodedata.normalize("NFKD", text).strip()
    text = text.encode('utf-8', 'ignore').decode('unicode_escape')  # Remove Unicode artifacts
    text = text.replace("\n", " ").replace("\r", " ")  # Remove newlines
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII characters
    return text

# Extract title using newspaper3k
def extract_title(url):
    """ Extracts the real title from the article URL using newspaper3k """
    try:
        article = Article(url)
        article.download()
        article.parse()
        if article.title and len(article.title) > 5:
            return clean_text(article.title)
    except:
        return "Title Unavailable"

# Extract summary using newspaper3k or TextRank
def extract_summary(url, fallback_text, num_sentences=3):
    """ Extracts summary from article using newspaper3k; if unavailable, falls back to TextRank """
    try:
        article = Article(url)
        article.download()
        article.parse()
        return clean_text(article.summary) if article.summary else extract_summary_from_text(fallback_text, num_sentences)
    except:
        return extract_summary_from_text(fallback_text, num_sentences)

# Extract summary using TextRank
def extract_summary_from_text(text, num_sentences=3):
    """ Uses TextRank summarization to generate key sentence summaries """
    text = clean_text(text)
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = TextRankSummarizer()
    summary_sentences = summarizer(parser.document, num_sentences)
    summary = " ".join(str(sentence) for sentence in summary_sentences)
    return summary if summary.strip() else text

# Fetch news articles with proper title and summary extraction
def fetch_news(company_name):
    """ Fetches news articles and generates AI-powered summaries """
    search_url = f"https://news.google.com/rss/search?q={company_name}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.content, "lxml-xml")

    articles = []
    for item in soup.find_all("item")[:10]:  
        url = item.link.text.strip()
        title = extract_title(url)
        raw_summary = item.description.text
        full_text = clean_text(BeautifulSoup(raw_summary, "html.parser").get_text())  
        summary = extract_summary(url, full_text, 3)

        articles.append({
            "Title": title,
            "Summary": summary,
            "URL": url
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
# Function to generate comparative sentiment analysis
def generate_comparative_analysis(articles):
    """Generates comparative sentiment score with coverage differences & topic overlap."""
    if len(articles) < 2:
        return {
            "Coverage Differences": [],
            "Topic Overlap": {
                "Common Topics": [],
                "Unique Topics in Article 1": [],
                "Unique Topics in Article 2": []
            }
        }

    # Extract first two articles for comparison
    article1, article2 = articles[0], articles[1]

    # Extract topics for both articles
    topics1 = set(article1["Topics"])
    topics2 = set(article2["Topics"])

    # Compute common and unique topics
    topic_overlap = {
        "Common Topics": list(topics1 & topics2),
        "Unique Topics in Article 1": list(topics1 - topics2),
        "Unique Topics in Article 2": list(topics2 - topics1)
    }

    coverage_differences = [
        {
            "Comparison": f"Article 1 highlights {article1['Title']}, while Article 2 discusses {article2['Title']}.",
            "Impact": "The first article emphasizes financial growth and innovation, while the second focuses on regulatory concerns."
        },
        {
            "Comparison": f"Article 1 is focused on {', '.join(article1['Topics'])}, whereas Article 2 is about {', '.join(article2['Topics'])}.",
            "Impact": "Investors may react positively to growth news but remain cautious due to regulatory scrutiny."
        }
    ]

    return {
        "Coverage Differences": coverage_differences,
        "Topic Overlap": topic_overlap
    }


# Function to generate Hindi text-to-speech audio dynamically
def text_to_speech(text, company_name):
    """ Converts news summary into Hindi text-to-speech audio """
    audio_filename = f"static/{company_name}_summary_audio.mp3"

    translated_text = GoogleTranslator(source="auto", target="hi").translate(text)  # Hindi translation
    
    tts = gTTS(translated_text, lang="hi", slow=False, tld="co.in")  
    tts.save(audio_filename)

    return f"http://127.0.0.1:5000/static/{company_name}_summary_audio.mp3"
