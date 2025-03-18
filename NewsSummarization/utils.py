# utils.py

import os
import tempfile
from gtts import gTTS
from transformers import pipeline

# Initialize the summarization pipeline (using a model such as Facebook's BART)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text, max_length=150, min_length=30):
    """
    Summarize the given text using a transformer-based summarization model.
    Returns a summarized version of the input text.
    """
    if not text:
        return ""
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']

def convert_text_to_speech(text, lang="hi", filename="output.mp3"):
    """
    Convert text to speech (Hindi by default) using gTTS.
    Saves the generated audio file to a temporary directory and returns its path.
    """
    tts = GtTS(text=text, lang=lang)
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    tts.save(file_path)
    return file_path

def extract_topics(text, num_topics=3):
    """
    Extract key topics from the provided text.
    (This is a simplified placeholder. In practice, you might use RAKE, spaCy, or KeyBERT.)
    """
    if not text:
        return []
    # For demonstration, split text into words and return the first few longer words.
    words = [word.strip('.,') for word in text.split() if len(word) > 4]
    unique_words = list(dict.fromkeys(words))
    return unique_words[:num_topics]

def comparative_sentiment_analysis(articles):
    """
    Given a list of articles (each with a 'sentiment_label'), compute a simple sentiment distribution.
    Returns a dictionary with counts for "Positive", "Negative", and "Neutral".
    """
    distribution = {"Positive": 0, "Negative": 0, "Neutral": 0}
    for article in articles:
        label = article.get("sentiment_label", "Neutral")
        if label in distribution:
            distribution[label] += 1
    return distribution
