import numpy as np
from typing import Dict, List, Optional, Tuple
from transformers import pipeline
import json
from .base import BaseAIService
from app.core.config import settings

class SentimentAnalysisService(BaseAIService):
    """AI service for sentiment analysis of customer communications."""
    
    def __init__(self):
        super().__init__()
        self.sentiment_pipeline = None
        self.emotion_pipeline = None
        self._load_models()
    
    def _load_models(self):
        """Load sentiment analysis models."""
        try:
            # Load sentiment analysis pipeline
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=settings.SENTIMENT_MODEL,
                device=self.device
            )
            print(f"Loaded sentiment model: {settings.SENTIMENT_MODEL}")
            
        except Exception as e:
            print(f"Error loading sentiment models: {e}")
            self.sentiment_pipeline = None
    
    def analyze_sentiment(self, text: str) -> Dict[str, any]:
        """Analyze sentiment of a given text."""
        if not text or not text.strip():
            return {
                "sentiment": "neutral",
                "score": 0.5,
                "confidence": 0.0,
                "emotions": {},
                "key_phrases": [],
                "overall_tone": "neutral"
            }
        
        # Clean text
        cleaned_text = self._clean_text(text)
        
        # Get sentiment analysis
        sentiment_result = self._get_sentiment(cleaned_text)
        
        # Get emotions
        emotions = self._extract_emotions(cleaned_text)
        
        # Extract key phrases
        key_phrases = self._extract_key_phrases(cleaned_text)
        
        # Determine overall tone
        overall_tone = self._determine_overall_tone(sentiment_result, emotions)
        
        return {
            "sentiment": sentiment_result["label"],
            "score": sentiment_result["score"],
            "confidence": sentiment_result["score"],
            "emotions": emotions,
            "key_phrases": key_phrases,
            "overall_tone": overall_tone,
            "raw_text": text,
            "cleaned_text": cleaned_text
        }
    
    def _get_sentiment(self, text: str) -> Dict[str, any]:
        """Get sentiment analysis using the pipeline."""
        if self.sentiment_pipeline is None:
            # Fallback sentiment analysis
            return self._fallback_sentiment_analysis(text)
        
        try:
            # Split long text into chunks if needed
            if len(text) > 500:
                chunks = self._split_text(text, max_length=500)
                results = []
                for chunk in chunks:
                    result = self.sentiment_pipeline(chunk)[0]
                    results.append(result)
                
                # Aggregate results
                return self._aggregate_sentiment_results(results)
            else:
                result = self.sentiment_pipeline(text)[0]
                return {
                    "label": result["label"],
                    "score": result["score"]
                }
                
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return self._fallback_sentiment_analysis(text)
    
    def _fallback_sentiment_analysis(self, text: str) -> Dict[str, any]:
        """Fallback sentiment analysis using simple keyword matching."""
        text_lower = text.lower()
        
        # Positive keywords
        positive_words = [
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'like', 'happy', 'satisfied', 'pleased', 'thank', 'thanks',
            'awesome', 'perfect', 'outstanding', 'superb', 'brilliant'
        ]
        
        # Negative keywords
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'disappointed', 'angry',
            'frustrated', 'upset', 'hate', 'dislike', 'poor', 'worst',
            'unhappy', 'dissatisfied', 'annoyed', 'irritated', 'mad'
        ]
        
        # Count occurrences
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Calculate sentiment
        total_words = len(text.split())
        if total_words == 0:
            return {"label": "neutral", "score": 0.5}
        
        positive_ratio = positive_count / total_words
        negative_ratio = negative_count / total_words
        
        if positive_ratio > negative_ratio:
            sentiment = "positive"
            score = min(0.9, 0.5 + positive_ratio)
        elif negative_ratio > positive_ratio:
            sentiment = "negative"
            score = min(0.9, 0.5 + negative_ratio)
        else:
            sentiment = "neutral"
            score = 0.5
        
        return {"label": sentiment, "score": score}
    
    def _extract_emotions(self, text: str) -> Dict[str, float]:
        """Extract emotions from text using keyword analysis."""
        text_lower = text.lower()
        
        emotions = {
            "joy": 0.0,
            "sadness": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "surprise": 0.0,
            "disgust": 0.0,
            "trust": 0.0,
            "anticipation": 0.0
        }
        
        # Emotion keywords
        emotion_keywords = {
            "joy": ["happy", "joy", "excited", "thrilled", "delighted", "pleased"],
            "sadness": ["sad", "disappointed", "upset", "depressed", "unhappy", "grief"],
            "anger": ["angry", "mad", "furious", "irritated", "annoyed", "frustrated"],
            "fear": ["afraid", "scared", "worried", "anxious", "terrified", "nervous"],
            "surprise": ["surprised", "shocked", "amazed", "astonished", "stunned"],
            "disgust": ["disgusted", "revolted", "appalled", "sickened"],
            "trust": ["trust", "confident", "reliable", "secure", "safe"],
            "anticipation": ["excited", "eager", "looking forward", "anticipate"]
        }
        
        # Count emotion keywords
        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                emotions[emotion] = min(1.0, count * 0.2)  # Normalize to 0-1
        
        return emotions
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text."""
        # Simple approach: extract phrases with important words
        important_words = [
            'problem', 'issue', 'concern', 'complaint', 'request', 'question',
            'help', 'support', 'service', 'product', 'price', 'quality',
            'delivery', 'refund', 'cancel', 'order', 'payment', 'account'
        ]
        
        sentences = text.split('.')
        key_phrases = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(word in sentence_lower for word in important_words):
                # Clean and add the sentence
                cleaned_sentence = sentence.strip()
                if len(cleaned_sentence) > 10:  # Only add meaningful phrases
                    key_phrases.append(cleaned_sentence)
        
        return key_phrases[:5]  # Limit to top 5 phrases
    
    def _determine_overall_tone(self, sentiment_result: Dict, emotions: Dict[str, float]) -> str:
        """Determine overall tone based on sentiment and emotions."""
        sentiment = sentiment_result["label"]
        score = sentiment_result["score"]
        
        # Get dominant emotion
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])
        
        if sentiment == "positive" and score > 0.7:
            if dominant_emotion[1] > 0.5:
                return f"very_positive_{dominant_emotion[0]}"
            else:
                return "very_positive"
        elif sentiment == "positive":
            return "positive"
        elif sentiment == "negative" and score > 0.7:
            if dominant_emotion[1] > 0.5:
                return f"very_negative_{dominant_emotion[0]}"
            else:
                return "very_negative"
        elif sentiment == "negative":
            return "negative"
        else:
            return "neutral"
    
    def _split_text(self, text: str, max_length: int = 500) -> List[str]:
        """Split long text into smaller chunks."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > max_length:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [word]
                    current_length = len(word)
                else:
                    # Single word is too long, add it anyway
                    chunks.append(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def _aggregate_sentiment_results(self, results: List[Dict]) -> Dict[str, any]:
        """Aggregate sentiment results from multiple chunks."""
        if not results:
            return {"label": "neutral", "score": 0.5}
        
        # Count sentiments
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        total_score = 0.0
        
        for result in results:
            sentiment_counts[result["label"]] += 1
            total_score += result["score"]
        
        # Determine dominant sentiment
        dominant_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])[0]
        
        # Calculate average score
        avg_score = total_score / len(results)
        
        return {
            "label": dominant_sentiment,
            "score": avg_score
        }
    
    def analyze_conversation_sentiment(self, messages: List[Dict]) -> Dict[str, any]:
        """Analyze sentiment across a conversation."""
        if not messages:
            return {
                "overall_sentiment": "neutral",
                "sentiment_trend": "stable",
                "average_sentiment": 0.5,
                "sentiment_changes": 0,
                "key_moments": []
            }
        
        sentiments = []
        sentiment_scores = []
        
        for message in messages:
            text = message.get("content", "")
            if text:
                sentiment_result = self.analyze_sentiment(text)
                sentiments.append(sentiment_result["sentiment"])
                sentiment_scores.append(sentiment_result["score"])
        
        if not sentiment_scores:
            return {
                "overall_sentiment": "neutral",
                "sentiment_trend": "stable",
                "average_sentiment": 0.5,
                "sentiment_changes": 0,
                "key_moments": []
            }
        
        # Calculate overall sentiment
        avg_score = np.mean(sentiment_scores)
        if avg_score > 0.6:
            overall_sentiment = "positive"
        elif avg_score < 0.4:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"
        
        # Calculate sentiment trend
        sentiment_trend = self._calculate_sentiment_trend(sentiment_scores)
        
        # Count sentiment changes
        sentiment_changes = self._count_sentiment_changes(sentiments)
        
        # Identify key moments
        key_moments = self._identify_key_moments(messages, sentiment_scores)
        
        return {
            "overall_sentiment": overall_sentiment,
            "sentiment_trend": sentiment_trend,
            "average_sentiment": round(avg_score, 3),
            "sentiment_changes": sentiment_changes,
            "key_moments": key_moments,
            "sentiment_distribution": {
                "positive": sentiments.count("positive"),
                "negative": sentiments.count("negative"),
                "neutral": sentiments.count("neutral")
            }
        }
    
    def _calculate_sentiment_trend(self, scores: List[float]) -> str:
        """Calculate sentiment trend over time."""
        if len(scores) < 2:
            return "stable"
        
        # Calculate trend using linear regression
        x = np.arange(len(scores))
        slope = np.polyfit(x, scores, 1)[0]
        
        if slope > 0.05:
            return "improving"
        elif slope < -0.05:
            return "declining"
        else:
            return "stable"
    
    def _count_sentiment_changes(self, sentiments: List[str]) -> int:
        """Count the number of sentiment changes in a conversation."""
        if len(sentiments) < 2:
            return 0
        
        changes = 0
        for i in range(1, len(sentiments)):
            if sentiments[i] != sentiments[i-1]:
                changes += 1
        
        return changes
    
    def _identify_key_moments(self, messages: List[Dict], sentiment_scores: List[float]) -> List[Dict]:
        """Identify key moments in the conversation."""
        key_moments = []
        
        if len(sentiment_scores) < 2:
            return key_moments
        
        # Find significant sentiment changes
        for i in range(1, len(sentiment_scores)):
            change = abs(sentiment_scores[i] - sentiment_scores[i-1])
            if change > 0.3:  # Significant change threshold
                key_moments.append({
                    "index": i,
                    "message": messages[i].get("content", "")[:100] + "...",
                    "sentiment_change": round(change, 3),
                    "new_sentiment": "positive" if sentiment_scores[i] > 0.6 else "negative" if sentiment_scores[i] < 0.4 else "neutral"
                })
        
        return key_moments[:3]  # Return top 3 key moments 