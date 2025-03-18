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
import json
from collections import Counter
from itertools import combinations

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
        return "Title Unavailable"
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
    return summary if summary.strip() else text[:200] + "..."  # Limit to 200 chars if no summary

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
        if title == "Google News":  # Skip generic titles
            continue
            
        raw_summary = item.description.text
        full_text = clean_text(BeautifulSoup(raw_summary, "html.parser").get_text())  
        summary = extract_summary(url, full_text, 3)

        articles.append({
            "Title": title,
            "Summary": summary,
        })

    return articles[:10]  # Ensure we return at most 10 articles

# Function to analyze sentiment dynamically for any text
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    return "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"

# Function to extract meaningful topics from article summaries
def extract_topics(summary, company_name):
    """Extract meaningful topics from article summaries with company-specific context"""
    # Extract potential topics
    words = re.findall(r'\b[A-Za-z]{3,}\b', summary.lower())
    keywords = [word for word in words if word not in STOPWORDS and word != company_name.lower()]
    
    # Define generic categories
    categories = {
        'financial': ['Stock', 'Investment', 'Financial', 'Revenue', 'Profit', 'Sales', 'Market'],
        'technology': ['Technology', 'Innovation', 'Digital', 'Software', 'Hardware', 'Engineering'],
        'business': ['Business', 'Strategy', 'Management', 'Growth', 'Development', 'Partnership'],
        'product': ['Product', 'Service', 'Launch', 'Release', 'Design', 'Quality'],
        'regulation': ['Regulation', 'Compliance', 'Legal', 'Government', 'Policy', 'Approval'],
        'competition': ['Competition', 'Competitor', 'Market Share', 'Industry', 'Rival'],
        'leadership': ['Leadership', 'Executive', 'CEO', 'Management', 'Board', 'Decision'],
        'international': ['International', 'Global', 'Export', 'Import', 'Foreign', 'Overseas'],
        'sustainability': ['Sustainability', 'Environment', 'Green', 'Climate', 'Carbon', 'Clean'],
        'workforce': ['Workforce', 'Employee', 'Labor', 'Job', 'Worker', 'Staff']
    }
    
    # Prioritize important keywords
    prioritized_keywords = []
    for word in keywords:
        for category, terms in categories.items():
            if any(term.lower() in word for term in terms):
                prioritized_keywords.append((word, category))
    
    # If no prioritized keywords found, use the raw keywords
    if not prioritized_keywords:
        # Convert keywords to title case and take the first 3
        return [keyword.title() for keyword in keywords[:3]] if keywords else ["General News"]
    
    # Group by category
    categorized_topics = {}
    for word, category in prioritized_keywords:
        if category not in categorized_topics:
            categorized_topics[category] = []
        categorized_topics[category].append(word)
    
    # Generate topics from categories
    topics = []
    for category, words in categorized_topics.items():
        if category == 'financial':
            topics.append('Financial Performance')
        elif category == 'technology':
            topics.append('Technology & Innovation')
        elif category == 'business':
            topics.append('Business Strategy')
        elif category == 'product':
            topics.append('Product Development')
        elif category == 'regulation':
            topics.append('Regulatory Affairs')
        elif category == 'competition':
            topics.append('Market Competition')
        elif category == 'leadership':
            topics.append('Leadership & Management')
        elif category == 'international':
            topics.append('Global Operations')
        elif category == 'sustainability':
            topics.append('Sustainability')
        elif category == 'workforce':
            topics.append('Workforce Management')
    
    # Ensure we have at least some topics
    if not topics:
        topics = [keyword.title() for keyword in keywords[:3]] if keywords else ["Industry News"]
    
    # Return up to 3 unique topics
    return list(set(topics))[:3]

# Function to process articles with sentiment and topics
def process_articles(articles, company_name):
    """Add sentiment and topics to each article"""
    for article in articles:
        article["Sentiment"] = analyze_sentiment(article["Summary"])
        article["Topics"] = extract_topics(article["Summary"], company_name)
    
    return articles

# Generate the comparative analysis section
def generate_comparative_analysis(articles, company_name):
    """Generate a detailed comparative analysis of the articles"""
    # Sentiment distribution
    sentiment_dist = {"Positive": 0, "Negative": 0, "Neutral": 0}
    for article in articles:
        sentiment_dist[article["Sentiment"]] += 1
    
    # Find all topics across articles
    all_topics = []
    for article in articles:
        all_topics.extend(article["Topics"])
    
    # Find common topics (appearing in at least 2 articles)
    topic_counts = Counter(all_topics)
    common_topics = [topic for topic, count in topic_counts.items() if count >= 2]
    
    # Generate coverage differences
    coverage_differences = []
    
    # Compare pairs of articles with different sentiments
    positive_articles = [a for a in articles if a["Sentiment"] == "Positive"]
    negative_articles = [a for a in articles if a["Sentiment"] == "Negative"]
    neutral_articles = [a for a in articles if a["Sentiment"] == "Neutral"]
    
    # If we have both positive and negative articles, create comparisons
    if positive_articles and negative_articles:
        pos_article = positive_articles[0]
        neg_article = negative_articles[0]
        
        comparison_dict = {
            "Comparison": f"Some articles like '{pos_article['Title']}' present positive aspects of {company_name}, while others like '{neg_article['Title']}' highlight concerns.",
            "Impact": f"The positive coverage may boost confidence in {company_name}, while the negative coverage raises important concerns that could affect investor perception."
        }
        coverage_differences.append(comparison_dict)
    
    # If we have a mix of sentiment types, add one more comparison
    if len(set([a["Sentiment"] for a in articles])) > 1:
        # Find two articles with different topics
        for a1, a2 in combinations(articles[:5], 2):
            if not set(a1["Topics"]).intersection(set(a2["Topics"])):
                comparison_dict = {
                    "Comparison": f"'{a1['Title']}' focuses on {', '.join(a1['Topics'])}, whereas '{a2['Title']}' addresses {', '.join(a2['Topics'])}.",
                    "Impact": f"This shows the diverse aspects of {company_name} covered in media, giving a multifaceted view of its operations and challenges."
                }
                coverage_differences.append(comparison_dict)
                break
    
    # If we don't have enough comparisons yet, add a generic one
    if len(coverage_differences) < 2:
        if len(articles) >= 2:
            a1, a2 = articles[0], articles[1]
            comparison_dict = {
                "Comparison": f"Articles like '{a1['Title']}' and '{a2['Title']}' present different perspectives on {company_name}.",
                "Impact": f"These different perspectives help build a more complete understanding of {company_name}'s market position and challenges."
            }
            coverage_differences.append(comparison_dict)
    
    # Find unique topics for different articles
    unique_topics_1 = []
    unique_topics_2 = []
    
    if len(articles) >= 2:
        unique_topics_1 = [t for t in articles[0]["Topics"] if t not in articles[1]["Topics"]]
        unique_topics_2 = [t for t in articles[1]["Topics"] if t not in articles[0]["Topics"]]
    
    topic_overlap = {
        "Common Topics": common_topics if common_topics else ["No common topics found"],
        "Unique Topics in Article 1": unique_topics_1 if unique_topics_1 else ["No unique topics"],
        "Unique Topics in Article 2": unique_topics_2 if unique_topics_2 else ["No unique topics"]
    }
    
    # Return the complete comparative analysis
    return {
        "Sentiment Distribution": sentiment_dist,
        "Coverage Differences": coverage_differences,
        "Topic Overlap": topic_overlap
    }

# Generate final sentiment analysis
def generate_final_sentiment(sentiment_dist, company_name):
    """Generate a final sentiment analysis summary"""
    total = sum(sentiment_dist.values())
    if total == 0:
        return f"No news coverage found for {company_name}."
    
    positive_percent = (sentiment_dist["Positive"] / total) * 100
    negative_percent = (sentiment_dist["Negative"] / total) * 100
    neutral_percent = (sentiment_dist["Neutral"] / total) * 100
    
    if positive_percent > negative_percent + 10:
        return f"{company_name}'s latest news coverage is mostly positive ({positive_percent:.0f}%). Potential growth expectations are favorable."
    elif negative_percent > positive_percent + 10:
        return f"{company_name}'s latest news coverage is predominantly negative ({negative_percent:.0f}%). Potential challenges ahead."
    else:
        return f"{company_name}'s latest news coverage is mixed or neutral. Market sentiment appears balanced."

# Function to generate Hindi text-to-speech audio dynamically
def text_to_speech(text, company_name):
    """ Converts news summary into Hindi text-to-speech audio """
    # Create static directory if it doesn't exist
    if not os.path.exists("static"):
        os.makedirs("static")
        
    audio_filename = f"static/{company_name}_summary_audio.mp3"
    
    # Ensure the text is a reasonable length for translation
    if len(text) > 1000:
        text = text[:1000] + "..."

    translated_text = GoogleTranslator(source="auto", target="hi").translate(text)  # Hindi translation
    
    tts = gTTS(translated_text, lang="hi", slow=False, tld="co.in")
    tts.save(audio_filename)

    return f"http://127.0.0.1:5000/static/{company_name}_summary_audio.mp3"

# Main function to process news for a company
def process_company_news(company_name):
    """Process all news for a given company and return structured data"""
    # Fetch news articles
    articles = fetch_news(company_name)
    
    # Process articles with sentiment and topics
    processed_articles = process_articles(articles, company_name)
    
    # Calculate sentiment distribution
    sentiment_dist = {"Positive": 0, "Negative": 0, "Neutral": 0}
    for article in processed_articles:
        sentiment_dist[article["Sentiment"]] += 1
    
    # Generate comparative analysis
    comparative_analysis = generate_comparative_analysis(processed_articles, company_name)
    
    # Generate final sentiment analysis
    final_sentiment = generate_final_sentiment(sentiment_dist, company_name)
    
    # Generate text summary for TTS
    tts_summary = f"News analysis for {company_name}. {final_sentiment} "
    tts_summary += f"Out of {len(processed_articles)} articles analyzed, {sentiment_dist['Positive']} were positive, "
    tts_summary += f"{sentiment_dist['Negative']} were negative, and {sentiment_dist['Neutral']} were neutral. "
    
    # Add key topics
    all_topics = []
    for article in processed_articles:
        all_topics.extend(article["Topics"])
    
    top_topics = [topic for topic, _ in Counter(all_topics).most_common(3)]
    if top_topics:
        tts_summary += f"The main topics discussed were {', '.join(top_topics)}."
    
    # Generate TTS audio
    audio_url = text_to_speech(tts_summary, company_name)
    
    # Prepare final output
    result = {
        "Company": company_name,
        "Articles": processed_articles,
        "Comparative Sentiment Score": comparative_analysis,
        "Final Sentiment Analysis": final_sentiment,
        "Audio": audio_url
    }
    
    return result
