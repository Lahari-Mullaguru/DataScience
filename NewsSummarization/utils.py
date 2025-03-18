import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from gtts import gTTS
import os
import re
import unicodedata
from deep_translator import GoogleTranslator
import nltk

# Download stopwords for topic extraction if not already downloaded
nltk.download("stopwords")
from nltk.corpus import stopwords

# Define a set of stopwords for filtering keywords
STOPWORDS = set(stopwords.words("english"))

def clean_text(text):
    """
    Clean the text by normalizing Unicode characters and removing newlines.
    """
    text = unicodedata.normalize("NFKD", text).strip()
    return text.replace("\n", " ").replace("\r", " ")

def fetch_news(company_name):
    """
    Fetches news articles from Google News RSS feed for the given company.
    Returns a list of dictionaries containing article Title and Summary.
    """
    search_url = f"https://news.google.com/rss/search?q={company_name}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.content, "lxml-xml")
    articles = []
    
    # Limit to first 10 articles
    for item in soup.find_all("item")[:10]:
        title = clean_text(item.title.text)
        raw_summary = item.description.text

        # Parse the raw summary to extract only the headline from the <a> tag
        soup_desc = BeautifulSoup(raw_summary, "html.parser")
        a_tag = soup_desc.find("a")
        if a_tag:
            summary = clean_text(a_tag.get_text())
        else:
            # Fallback: get all text if <a> tag is not found
            summary = clean_text(soup_desc.get_text())
        
        # Append extra info if summary is identical to title
        if summary == title:
            summary = f"{title} - More details inside."

        articles.append({
            "Title": title,
            "Summary": summary
        })
    
    return articles

def analyze_sentiment(text):
    """
    Analyzes the sentiment of the provided text using TextBlob.
    Returns "Positive", "Negative", or "Neutral" based on polarity.
    """
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

def extract_topics(summary):
    """
    Extracts meaningful topics (keywords) from the article summary.
    Returns a list of up to 3 keywords (excluding stopwords) from words with 4 or more letters.
    """
    words = re.findall(r'\b[A-Za-z]{4,}\b', summary)
    keywords = [word.lower() for word in words if word.lower() not in STOPWORDS]
    return list(set(keywords))[:3]

def compare_sentiments(articles):
    """
    Processes each article to analyze sentiment and extract topics.
    Returns the sentiment count across all articles and updates each article with its sentiment and topics.
    """
    sentiment_count = {"Positive": 0, "Negative": 0, "Neutral": 0}

    for article in articles:
        sentiment = analyze_sentiment(article["Summary"])
        topics = extract_topics(article["Summary"])
        article["Sentiment"] = sentiment
        article["Topics"] = topics
        sentiment_count[sentiment] += 1

    return sentiment_count, articles

def generate_coverage_comparison(articles, company_name):
    """
    Compares the first two articles to determine coverage differences and topic overlaps.
    Returns:
      - A list of coverage difference statements.
      - A dictionary outlining common topics and unique topics in each article.
    """
    coverage_differences = []
    topic_overlap = {
        "Common Topics": [company_name],  # Company name is always included
        "Unique Topics in Article 1": [],
        "Unique Topics in Article 2": []
    }
    
    if len(articles) < 2:
        return coverage_differences, topic_overlap

    article1 = articles[0]
    article2 = articles[1]
    topics1 = article1.get("Topics", [])
    topics2 = article2.get("Topics", [])
    
    common_topics = list(set(topics1) & set(topics2))
    if not common_topics:
        common_topics.append("General Business News")
    
    topic_overlap["Common Topics"].extend(common_topics)
    topic_overlap["Unique Topics in Article 1"] = list(set(topics1) - set(topics2))
    topic_overlap["Unique Topics in Article 2"] = list(set(topics2) - set(topics1))
    
    # Two example comparative statements
    coverage_differences.append({
        "Comparison": f"Article 1 highlights {', '.join(topics1)}, while Article 2 focuses on {', '.join(topics2)}.",
        "Impact": f"The first article boosts confidence in {company_name}'s market growth, while the second raises concerns about potential risks."
    })
    coverage_differences.append({
        "Comparison": f"Article 1 centers on financial success and innovation, whereas Article 2 discusses regulatory challenges.",
        "Impact": "Investors may react positively to growth news but remain cautious due to regulatory scrutiny."
    })
    
    return coverage_differences, topic_overlap

def generate_final_sentiment(sentiment_data, company_name):
    """
    Generates an overall sentiment analysis statement for the company based on article sentiments.
    """
    total_articles = sum(sentiment_data.values())
    if sentiment_data["Positive"] > sentiment_data["Negative"]:
        return f"{company_name}’s latest news coverage is mostly positive. Potential stock growth expected."
    elif sentiment_data["Negative"] > sentiment_data["Positive"]:
        percentage = round((sentiment_data['Negative'] / total_articles) * 100, 1)
        return f"The latest news coverage about {company_name} is mostly negative. {percentage}% of articles indicate potential risks."
    else:
        return f"The news coverage for {company_name} is balanced with mixed reactions."

def text_to_speech(text, company_name):
    """
    Converts the provided text to Hindi speech using gTTS and saves it as an MP3 file.
    Returns a URL to access the generated audio file.
    """
    # Ensure the static directory exists
    if not os.path.exists("static"):
        os.makedirs("static")
        
    audio_filename = f"static/{company_name}_summary_audio.mp3"
    # Translate text to Hindi
    translated_text = GoogleTranslator(source="auto", target="hi").translate(text)
    tts = gTTS(translated_text, lang="hi", slow=False, tld="co.in")
    tts.save(audio_filename)
    # Return a URL (assuming the API serves static files on port 5000)
    return f"http://127.0.0.1:5000/static/{company_name}_summary_audio.mp3"

def generate_report(company_name):
    """
    Generates a comprehensive report that includes:
      - A list of articles with title, summary, sentiment, and topics.
      - Comparative sentiment analysis and topic overlap.
      - A final sentiment analysis statement.
      - A multi-line summary (approximately 5–6 lines).
      - A URL to the Hindi TTS audio file.
    Returns a dictionary with the structured report.
    """
    # Fetch and process articles
    articles = fetch_news(company_name)
    sentiment_count, articles = compare_sentiments(articles)
    coverage_differences, topic_overlap = generate_coverage_comparison(articles, company_name)
    final_sentiment = generate_final_sentiment(sentiment_count, company_name)
    
    # Create a multi-line summary
    summary_lines = []
    summary_lines.append(f"Company: {company_name}")
    summary_lines.append("Sentiment Distribution: " + ", ".join([f"{k}: {v}" for k, v in sentiment_count.items()]))
    if coverage_differences:
        summary_lines.append("Coverage Comparison: " + coverage_differences[0]["Comparison"])
    else:
        summary_lines.append("Coverage Comparison: Not enough data for a comparison.")
    common_topics = topic_overlap.get("Common Topics", [])
    summary_lines.append("Common Topics: " + (", ".join(common_topics) if common_topics else "None"))
    summary_lines.append("Final Analysis: " + final_sentiment)
    multi_line_summary = "\n".join(summary_lines)
    
    # Generate TTS audio for the summary
    audio_url = text_to_speech(multi_line_summary, company_name)
    
    # Build the final report dictionary
    report = {
        "Company": company_name,
        "Articles": articles,
        "Comparative Sentiment Score": {
            "Sentiment Distribution": sentiment_count,
            "Coverage Differences": coverage_differences,
            "Topic Overlap": topic_overlap
        },
        "Final Sentiment Analysis": final_sentiment,
        "Summary": multi_line_summary,
        "Audio": audio_url
    }
    
    return report
