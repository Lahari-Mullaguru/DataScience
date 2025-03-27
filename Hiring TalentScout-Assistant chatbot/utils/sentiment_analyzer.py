from transformers import pipeline
from typing import Dict, Optional
import warnings

# Suppress warnings about model loading
warnings.filterwarnings("ignore")

class SentimentAnalyzer:
    def __init__(self):
        """Initialize sentiment analysis pipeline"""
        try:
            self.analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
        except Exception as e:
            print(f"Failed to load sentiment analyzer: {e}")
            self.analyzer = None

    def analyze_conversation(self, messages: list) -> Optional[Dict]:
        """
        Analyze conversation sentiment
        Returns:
            {
                "overall_sentiment": "POSITIVE/NEGATIVE/NEUTRAL",
                "confidence": float,
                "warning": bool (if negative detected)
            }
        """
        if not self.analyzer:
            return None

        full_text = " ".join([msg["content"] for msg in messages])
        
        try:
            result = self.analyzer(full_text)[0]
            return {
                "overall_sentiment": result["label"],
                "confidence": result["score"],
                "warning": result["label"] == "NEGATIVE" and result["score"] > 0.7
            }
        except Exception as e:
            print(f"Sentiment analysis failed: {e}")
            return None

# Singleton instance
sentiment_analyzer = SentimentAnalyzer()
