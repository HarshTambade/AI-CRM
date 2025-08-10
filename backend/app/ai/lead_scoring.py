import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
from datetime import datetime, timedelta

from .base import BaseAIService
from app.core.config import settings

class LeadScoringService(BaseAIService):
    """AI service for lead scoring and conversion prediction."""
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.model_path = os.path.join(settings.HUGGINGFACE_CACHE_DIR, "lead_scoring_model.pkl")
        self.scaler_path = os.path.join(settings.HUGGINGFACE_CACHE_DIR, "lead_scoring_scaler.pkl")
        self.encoders_path = os.path.join(settings.HUGGINGFACE_CACHE_DIR, "lead_scoring_encoders.pkl")
        
    def _extract_features(self, lead_data: Dict) -> Dict[str, float]:
        """Extract features from lead data for scoring."""
        features = {}
        
        # Basic lead information
        features['has_email'] = 1.0 if lead_data.get('email') else 0.0
        features['has_phone'] = 1.0 if lead_data.get('phone') else 0.0
        features['has_company'] = 1.0 if lead_data.get('company') else 0.0
        features['has_job_title'] = 1.0 if lead_data.get('job_title') else 0.0
        
        # Company size (estimated from company name)
        company = lead_data.get('company', '').lower()
        if any(word in company for word in ['inc', 'corp', 'llc', 'ltd']):
            features['company_size_score'] = 0.8
        elif any(word in company for word in ['enterprise', 'enterprises']):
            features['company_size_score'] = 1.0
        else:
            features['company_size_score'] = 0.5
        
        # Source scoring
        source = lead_data.get('source', '').lower()
        source_scores = {
            'website': 0.7,
            'referral': 0.9,
            'cold_call': 0.3,
            'email_campaign': 0.6,
            'social_media': 0.5,
            'trade_show': 0.8,
            'partner': 0.9
        }
        features['source_score'] = source_scores.get(source, 0.5)
        
        # Engagement features
        features['engagement_score'] = self._calculate_engagement_score(lead_data)
        
        # Budget and timeline
        budget = lead_data.get('budget', 0)
        features['budget_score'] = min(1.0, budget / 100000) if budget else 0.5
        
        timeline = lead_data.get('timeline', '').lower()
        timeline_scores = {
            'immediate': 0.9,
            'within_30_days': 0.8,
            'within_90_days': 0.6,
            'within_6_months': 0.4,
            'no_timeline': 0.2
        }
        features['timeline_score'] = timeline_scores.get(timeline, 0.3)
        
        # Activity-based features
        features['activity_count'] = lead_data.get('activity_count', 0)
        features['days_since_last_activity'] = lead_data.get('days_since_last_activity', 999)
        features['response_time_score'] = self._calculate_response_time_score(lead_data)
        
        return features
    
    def _calculate_engagement_score(self, lead_data: Dict) -> float:
        """Calculate engagement score based on lead activities."""
        activities = lead_data.get('activities', [])
        if not activities:
            return 0.0
        
        # Weight different activity types
        activity_weights = {
            'email': 0.3,
            'call': 0.5,
            'meeting': 0.8,
            'demo': 0.9,
            'proposal': 1.0
        }
        
        total_score = 0.0
        for activity in activities:
            activity_type = activity.get('type', '').lower()
            weight = activity_weights.get(activity_type, 0.1)
            total_score += weight
        
        # Normalize by number of activities
        return min(1.0, total_score / len(activities))
    
    def _calculate_response_time_score(self, lead_data: Dict) -> float:
        """Calculate response time score (faster = better)."""
        avg_response_time = lead_data.get('avg_response_time_hours', 999)
        
        if avg_response_time <= 1:
            return 1.0
        elif avg_response_time <= 4:
            return 0.8
        elif avg_response_time <= 24:
            return 0.6
        elif avg_response_time <= 72:
            return 0.4
        else:
            return 0.2
    
    def train_model(self, training_data: List[Dict]) -> Dict[str, float]:
        """Train the lead scoring model with historical data."""
        if not training_data:
            return {"error": "No training data provided"}
        
        # Prepare features and labels
        features_list = []
        labels = []
        
        for lead in training_data:
            features = self._extract_features(lead)
            features_list.append(features)
            
            # Convert status to binary (converted vs not converted)
            status = lead.get('status', '').lower()
            is_converted = 1 if status in ['closed_won', 'qualified'] else 0
            labels.append(is_converted)
        
        # Convert to DataFrame
        df = pd.DataFrame(features_list)
        
        # Handle missing values
        df = df.fillna(0.0)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            df, labels, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Save model
        self._save_model()
        
        return {
            "accuracy": accuracy,
            "feature_importance": dict(zip(df.columns, self.model.feature_importances_))
        }
    
    def predict_lead_score(self, lead_data: Dict) -> Dict[str, float]:
        """Predict lead score and conversion probability."""
        if self.model is None:
            self._load_model()
        
        if self.model is None:
            # Fallback scoring if model not available
            return self._fallback_scoring(lead_data)
        
        # Extract features
        features = self._extract_features(lead_data)
        feature_df = pd.DataFrame([features])
        feature_df = feature_df.fillna(0.0)
        
        # Scale features
        features_scaled = self.scaler.transform(feature_df)
        
        # Make prediction
        conversion_probability = self.model.predict_proba(features_scaled)[0][1]
        
        # Calculate lead score (0-100)
        lead_score = conversion_probability * 100
        
        # Calculate confidence based on feature completeness
        confidence = self._calculate_prediction_confidence(features)
        
        return {
            "lead_score": round(lead_score, 2),
            "conversion_probability": round(conversion_probability, 4),
            "confidence": round(confidence, 2),
            "risk_level": self._get_risk_level(lead_score),
            "recommendations": self._get_recommendations(lead_score, features)
        }
    
    def _fallback_scoring(self, lead_data: Dict) -> Dict[str, float]:
        """Fallback scoring when ML model is not available."""
        features = self._extract_features(lead_data)
        
        # Simple weighted scoring
        weights = {
            'has_email': 0.1,
            'has_phone': 0.1,
            'has_company': 0.15,
            'has_job_title': 0.1,
            'company_size_score': 0.15,
            'source_score': 0.2,
            'engagement_score': 0.3,
            'budget_score': 0.2,
            'timeline_score': 0.15,
            'activity_count': 0.1,
            'response_time_score': 0.1
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for feature, weight in weights.items():
            if feature in features:
                total_score += features[feature] * weight
                total_weight += weight
        
        lead_score = (total_score / total_weight) * 100 if total_weight > 0 else 50.0
        
        return {
            "lead_score": round(lead_score, 2),
            "conversion_probability": round(lead_score / 100, 4),
            "confidence": 0.5,  # Lower confidence for fallback
            "risk_level": self._get_risk_level(lead_score),
            "recommendations": self._get_recommendations(lead_score, features)
        }
    
    def _calculate_prediction_confidence(self, features: Dict[str, float]) -> float:
        """Calculate confidence in prediction based on feature completeness."""
        required_features = [
            'has_email', 'has_phone', 'has_company', 'has_job_title',
            'source_score', 'engagement_score', 'budget_score', 'timeline_score'
        ]
        
        available_features = sum(1 for f in required_features if f in features and features[f] > 0)
        confidence = available_features / len(required_features)
        
        return min(1.0, confidence + 0.2)  # Base confidence of 0.2
    
    def _get_risk_level(self, lead_score: float) -> str:
        """Get risk level based on lead score."""
        if lead_score >= 80:
            return "low"
        elif lead_score >= 60:
            return "medium"
        elif lead_score >= 40:
            return "high"
        else:
            return "very_high"
    
    def _get_recommendations(self, lead_score: float, features: Dict[str, float]) -> List[str]:
        """Get recommendations based on lead score and features."""
        recommendations = []
        
        if lead_score < 40:
            recommendations.append("High risk lead - consider disqualifying")
            recommendations.append("Focus on qualification before pursuing")
        
        if features.get('engagement_score', 0) < 0.3:
            recommendations.append("Low engagement - increase touch points")
            recommendations.append("Consider different communication channels")
        
        if features.get('response_time_score', 0) < 0.5:
            recommendations.append("Slow response times - improve follow-up process")
        
        if features.get('budget_score', 0) < 0.3:
            recommendations.append("Budget concerns - focus on value proposition")
        
        if lead_score >= 70:
            recommendations.append("High-value lead - prioritize follow-up")
            recommendations.append("Consider expedited sales process")
        
        return recommendations
    
    def _save_model(self):
        """Save the trained model and scaler."""
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            print(f"Model saved to {self.model_path}")
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def _load_model(self):
        """Load the trained model and scaler."""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                print("Lead scoring model loaded successfully")
            else:
                print("No trained model found")
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from the trained model."""
        if self.model is None:
            return {}
        
        return dict(zip(
            ['has_email', 'has_phone', 'has_company', 'has_job_title', 
             'company_size_score', 'source_score', 'engagement_score', 
             'budget_score', 'timeline_score', 'activity_count', 
             'days_since_last_activity', 'response_time_score'],
            self.model.feature_importances_
        )) 