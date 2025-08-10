import os
import torch
from typing import Optional, Dict, Any, List
from transformers import AutoTokenizer, AutoModel, pipeline
from sentence_transformers import SentenceTransformer
import numpy as np
from app.core.config import settings

class BaseAIService:
    """Base class for all AI services with common functionality."""
    
    def __init__(self):
        self.device = torch.device(settings.MODEL_DEVICE)
        self.models_cache = {}
        self.tokenizers_cache = {}
        
    def _load_model(self, model_name: str, model_type: str = "transformer") -> Any:
        """Load a model with caching."""
        cache_key = f"{model_name}_{model_type}"
        
        if cache_key not in self.models_cache:
            try:
                if model_type == "sentence_transformer":
                    model = SentenceTransformer(model_name, device=self.device)
                elif model_type == "pipeline":
                    model = pipeline(model_name, device=self.device)
                else:
                    model = AutoModel.from_pretrained(model_name)
                    model.to(self.device)
                    model.eval()
                
                self.models_cache[cache_key] = model
                print(f"Loaded model: {model_name}")
                
            except Exception as e:
                print(f"Error loading model {model_name}: {e}")
                return None
        
        return self.models_cache[cache_key]
    
    def _load_tokenizer(self, model_name: str) -> Optional[Any]:
        """Load a tokenizer with caching."""
        if model_name not in self.tokenizers_cache:
            try:
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.tokenizers_cache[model_name] = tokenizer
                print(f"Loaded tokenizer: {model_name}")
            except Exception as e:
                print(f"Error loading tokenizer {model_name}: {e}")
                return None
        
        return self.tokenizers_cache[model_name]
    
    def _get_embeddings(self, texts: List[str], model_name: str = None) -> np.ndarray:
        """Get embeddings for a list of texts."""
        if model_name is None:
            model_name = settings.SENTENCE_TRANSFORMER_MODEL
        
        model = self._load_model(model_name, "sentence_transformer")
        if model is None:
            return np.array([])
        
        try:
            embeddings = model.encode(texts, convert_to_tensor=True, device=self.device)
            return embeddings.cpu().numpy()
        except Exception as e:
            print(f"Error getting embeddings: {e}")
            return np.array([])
    
    def _calculate_similarity(self, text1: str, text2: str, model_name: str = None) -> float:
        """Calculate similarity between two texts."""
        embeddings = self._get_embeddings([text1, text2], model_name)
        if len(embeddings) < 2:
            return 0.0
        
        # Calculate cosine similarity
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        return float(similarity)
    
    def _batch_process(self, items: List[Any], batch_size: int = 32):
        """Process items in batches to manage memory."""
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text."""
        if not text:
            return ""
        
        # Basic text cleaning
        text = text.strip()
        text = text.lower()
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        return text
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text using simple frequency-based approach."""
        from collections import Counter
        import re
        
        # Clean text
        text = self._clean_text(text)
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Count frequency
        word_counts = Counter(words)
        
        # Return top keywords
        return [word for word, count in word_counts.most_common(max_keywords)]
    
    def _normalize_score(self, score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Normalize a score to a 0-1 range."""
        return max(min_val, min(max_val, score))
    
    def _calculate_confidence(self, scores: List[float]) -> float:
        """Calculate confidence based on score variance."""
        if not scores:
            return 0.0
        
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        
        # Higher confidence for lower variance
        confidence = 1.0 / (1.0 + std_score)
        return self._normalize_score(confidence) 