"""
Intent Classifier for Smart Agents
Classifies user queries to determine which agent should handle them
"""

import re
from typing import Dict, List, Optional
from enum import Enum


class IntentType(Enum):
    """Supported intent types"""
    REPO_ANALYSIS = "repo_analysis"
    SKILL_MATCHING = "skill_matching"
    BOUNTY_ESTIMATION = "bounty_estimation"
    USER_PROFILE = "user_profile"
    GENERAL_CHAT = "general_chat"
    UNKNOWN = "unknown"


class IntentClassifier:
    """
    Simple rule-based intent classifier
    
    Uses keyword matching and patterns to determine user intent
    """
    
    def __init__(self):
        # Intent patterns and keywords
        self.intent_patterns = {
            IntentType.REPO_ANALYSIS: [
                r"analyze.*repo",
                r"repo.*analysis",
                r"check.*repository",
                r"examine.*code",
                r"code.*quality",
                r"repository.*health",
                r"project.*structure",
                r"codebase.*analysis"
            ],
            IntentType.SKILL_MATCHING: [
                r"match.*skill",
                r"skill.*match",
                r"find.*developer",
                r"recommend.*developer",
                r"who.*can.*do",
                r"skill.*required",
                r"developer.*for",
                r"expert.*in"
            ],
            IntentType.BOUNTY_ESTIMATION: [
                r"estimate.*bounty",
                r"bounty.*estimate", 
                r"how.*much.*worth",
                r"price.*estimate",
                r"value.*of",
                r"cost.*estimate",
                r"bounty.*amount",
                r"reward.*estimate",
                r"how.*much.*pay",
                r"pay.*for",
                r"cost.*of",
                r"price.*for"
            ],
            IntentType.USER_PROFILE: [
                r"my.*profile",
                r"update.*profile",
                r"user.*profile",
                r"my.*skills",
                r"my.*preferences",
                r"profile.*settings",
                r"account.*info"
            ],
            IntentType.GENERAL_CHAT: [
                r"hello",
                r"hi",
                r"help",
                r"what.*can.*you.*do",
                r"how.*are.*you",
                r"thanks",
                r"thank.*you"
            ]
        }
        
        # Keywords for each intent
        self.intent_keywords = {
            IntentType.REPO_ANALYSIS: [
                "analyze", "analysis", "repository", "repo", "code", "codebase",
                "project", "structure", "quality", "health", "examine", "check"
            ],
            IntentType.SKILL_MATCHING: [
                "match", "skill", "developer", "expert", "recommend", "find",
                "who", "can", "do", "required", "needed"
            ],
            IntentType.BOUNTY_ESTIMATION: [
                "estimate", "bounty", "price", "value", "worth", "cost",
                "amount", "reward", "money", "payment"
            ],
            IntentType.USER_PROFILE: [
                "profile", "user", "account", "my", "settings", "preferences",
                "skills", "update", "change"
            ],
            IntentType.GENERAL_CHAT: [
                "hello", "hi", "help", "thanks", "thank", "how", "what"
            ]
        }
    
    def classify(self, query: str) -> Dict:
        """
        Classify user query intent
        
        Args:
            query: User input query
            
        Returns:
            Dict with intent, confidence, and metadata
        """
        query_lower = query.lower().strip()
        
        if not query_lower:
            return {
                "intent": IntentType.UNKNOWN,
                "confidence": 0.0,
                "reasoning": "Empty query"
            }
        
        # Check patterns first (higher confidence)
        pattern_matches = self._check_patterns(query_lower)
        if pattern_matches:
            return pattern_matches
        
        # Check keywords (lower confidence)
        keyword_matches = self._check_keywords(query_lower)
        if keyword_matches:
            return keyword_matches
        
        # Default to general chat
        return {
            "intent": IntentType.GENERAL_CHAT,
            "confidence": 0.3,
            "reasoning": "No specific patterns found, defaulting to general chat"
        }
    
    def _check_patterns(self, query: str) -> Optional[Dict]:
        """Check regex patterns for intent matching"""
        
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return {
                        "intent": intent_type,
                        "confidence": 0.9,
                        "reasoning": f"Matched pattern: {pattern}"
                    }
        
        return None
    
    def _check_keywords(self, query: str) -> Optional[Dict]:
        """Check keyword matches for intent"""
        
        intent_scores = {}
        
        for intent_type, keywords in self.intent_keywords.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword in query:
                    score += 1
                    matched_keywords.append(keyword)
            
            if score > 0:
                intent_scores[intent_type] = {
                    "score": score,
                    "keywords": matched_keywords,
                    "confidence": min(0.7, score * 0.2)  # Max 0.7 for keywords
                }
        
        if intent_scores:
            # Get best match
            best_intent = max(intent_scores.items(), key=lambda x: x[1]["score"])
            
            return {
                "intent": best_intent[0],
                "confidence": best_intent[1]["confidence"],
                "reasoning": f"Matched keywords: {', '.join(best_intent[1]['keywords'])}"
            }
        
        return None
    
    def get_supported_intents(self) -> List[str]:
        """Get list of supported intent types"""
        return [intent.value for intent in IntentType if intent != IntentType.UNKNOWN]
    
    def get_intent_description(self, intent: IntentType) -> str:
        """Get description for intent type"""
        descriptions = {
            IntentType.REPO_ANALYSIS: "Analyze repositories, code quality, and project structure",
            IntentType.SKILL_MATCHING: "Match developers with required skills",
            IntentType.BOUNTY_ESTIMATION: "Estimate bounty values and project costs",
            IntentType.USER_PROFILE: "Manage user profiles and preferences",
            IntentType.GENERAL_CHAT: "General conversation and help"
        }
        return descriptions.get(intent, "Unknown intent")


# Global instance
intent_classifier = IntentClassifier()


def classify_intent(query: str) -> Dict:
    """Convenience function to classify intent"""
    return intent_classifier.classify(query)