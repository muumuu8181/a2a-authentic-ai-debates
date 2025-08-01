"""
Quality Calculator - Real-time Debate Quality Metrics
=====================================================

Implements Luna's quality metrics design for detecting authentic AI conversations.
"""

import time
import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import statistics
import re
from collections import Counter

from .session_manager import DiscussionTurn, DebateSession


@dataclass
class TurnMetrics:
    """Metrics for a single discussion turn"""
    turn_number: int
    coherence_score: float
    relevance_score: float
    diversity_score: float
    authenticity_score: float
    response_time: float
    reference_count: int
    new_arguments: int
    linguistic_features: Dict[str, float]


@dataclass
class QualityReport:
    """Comprehensive quality report for a debate session"""
    overall_score: float
    coherence: float
    relevance: float
    engagement: float
    authenticity: float
    alerts: List[str]
    recommendations: List[str]
    timestamp: datetime


class QualityCalculator:
    """Calculate real-time quality metrics for AI debates"""
    
    # Thresholds based on Luna's design
    ALERT_THRESHOLDS = {
        'coherence_drop': 0.6,      # Alert if coherence < 60%
        'topic_drift': 0.7,         # Alert if drift > 70%
        'repetition': 0.5,          # Alert if diversity < 50%
        'fake_detection': 0.4,      # Alert if authenticity < 40%
    }
    
    def __init__(self):
        self.word_cache = {}  # Cache for performance
    
    def calculate_turn_metrics(
        self, 
        turn: DiscussionTurn, 
        session: DebateSession,
        topic: str
    ) -> TurnMetrics:
        """Calculate all metrics for a single turn"""
        
        # Get conversation history up to this turn
        history = [t for t in session.turn_history if t.turn_number < turn.turn_number]
        
        # Calculate individual metrics
        coherence = self._calculate_coherence(turn, history)
        relevance = self._calculate_relevance(turn, topic)
        diversity = self._calculate_diversity(turn, history)
        authenticity = self._calculate_authenticity(turn, session)
        
        # Extract linguistic features
        linguistic_features = self._extract_linguistic_features(turn.message)
        
        # Count references and new arguments
        reference_count = self._count_references(turn, history)
        new_arguments = self._count_new_arguments(turn, history)
        
        return TurnMetrics(
            turn_number=turn.turn_number,
            coherence_score=coherence,
            relevance_score=relevance,
            diversity_score=diversity,
            authenticity_score=authenticity,
            response_time=turn.response_time,
            reference_count=reference_count,
            new_arguments=new_arguments,
            linguistic_features=linguistic_features
        )
    
    def _calculate_coherence(self, turn: DiscussionTurn, history: List[DiscussionTurn]) -> float:
        """Context Retention Score (CRS) - How well agent remembers previous points"""
        if not history:
            return 1.0  # First turn is always coherent
        
        # Check for references to previous arguments
        references = 0
        keywords_from_history = set()
        
        # Extract key terms from history
        for h_turn in history[-3:]:  # Look at last 3 turns
            words = self._extract_keywords(h_turn.message)
            keywords_from_history.update(words)
        
        # Check how many historical keywords appear in current turn
        current_words = self._extract_keywords(turn.message)
        common_words = keywords_from_history.intersection(current_words)
        
        if keywords_from_history:
            coherence = len(common_words) / len(keywords_from_history)
            return min(coherence * 2, 1.0)  # Scale up but cap at 1.0
        return 0.8  # Default if no history keywords
    
    def _calculate_relevance(self, turn: DiscussionTurn, topic: str) -> float:
        """Topic Adherence Score (TAS) - How closely response relates to topic"""
        # Simple keyword-based relevance for now
        topic_words = self._extract_keywords(topic)
        turn_words = self._extract_keywords(turn.message)
        
        if not topic_words:
            return 0.5
        
        # Count topic word occurrences in turn
        relevance_count = sum(1 for word in turn_words if word in topic_words)
        relevance = relevance_count / len(topic_words)
        
        return min(relevance * 1.5, 1.0)  # Scale and cap
    
    def _calculate_diversity(self, turn: DiscussionTurn, history: List[DiscussionTurn]) -> float:
        """Response Diversity Index (RDI) - Prevents repetitive responses"""
        # Get agent's previous messages
        agent_history = [t for t in history if t.agent_id == turn.agent_id]
        
        if not agent_history:
            return 1.0  # First message is always diverse
        
        # Calculate vocabulary diversity
        all_words = []
        for t in agent_history + [turn]:
            all_words.extend(self._extract_keywords(t.message))
        
        if not all_words:
            return 0.5
        
        unique_words = len(set(all_words))
        total_words = len(all_words)
        
        diversity = unique_words / total_words
        return diversity
    
    def _calculate_authenticity(self, turn: DiscussionTurn, session: DebateSession) -> float:
        """Response Time Variance (RTV) + Linguistic Fingerprint"""
        # Luna's brilliant idea: Check response time variance
        response_times = [t.response_time for t in session.turn_history if t.response_time > 0]
        
        if len(response_times) < 3:
            return 0.8  # Not enough data yet
        
        # Calculate variance
        variance = statistics.variance(response_times)
        mean_time = statistics.mean(response_times)
        
        # Expected variance range (based on Luna's analysis of real data)
        expected_min = 0.3  # Below 0.3s suggests fake responses
        expected_max = 5.0  # Above 5.0s indicates abnormal delays
        
        if variance < expected_min:
            # Suspiciously consistent timing
            return 0.3
        elif variance > expected_max:
            # Unusual variance
            return 0.7
        else:
            # Natural variation
            return 1.0
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        # Remove common words and extract key terms
        common_words = {'は', 'が', 'を', 'に', 'で', 'と', 'の', 'から', 'まで', 
                       'the', 'is', 'are', 'was', 'were', 'been', 'be', 'have', 'has', 'had',
                       'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might'}
        
        # Simple word extraction
        words = re.findall(r'\w+', text.lower())
        keywords = [w for w in words if len(w) > 2 and w not in common_words]
        
        return keywords
    
    def _extract_linguistic_features(self, text: str) -> Dict[str, float]:
        """Extract linguistic fingerprint features"""
        features = {}
        
        # Sentence count and average length
        sentences = re.split(r'[。！？\.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        features['sentence_count'] = len(sentences)
        features['avg_sentence_length'] = sum(len(s) for s in sentences) / max(len(sentences), 1)
        
        # Punctuation usage
        features['exclamation_ratio'] = text.count('！') / max(len(text), 1)
        features['question_ratio'] = text.count('？') / max(len(text), 1)
        
        # Character type ratios
        hiragana = len(re.findall(r'[ぁ-ん]', text))
        katakana = len(re.findall(r'[ァ-ヴ]', text))
        kanji = len(re.findall(r'[一-龯]', text))
        total_chars = max(len(text), 1)
        
        features['hiragana_ratio'] = hiragana / total_chars
        features['katakana_ratio'] = katakana / total_chars
        features['kanji_ratio'] = kanji / total_chars
        
        return features
    
    def _count_references(self, turn: DiscussionTurn, history: List[DiscussionTurn]) -> int:
        """Count explicit references to previous arguments"""
        reference_patterns = [
            r'先ほど.*言った',
            r'前の.*主張',
            r'さっき.*述べた',
            r'you mentioned',
            r'you said',
            r'your point about'
        ]
        
        count = 0
        for pattern in reference_patterns:
            count += len(re.findall(pattern, turn.message, re.IGNORECASE))
        
        return count
    
    def _count_new_arguments(self, turn: DiscussionTurn, history: List[DiscussionTurn]) -> int:
        """Count new arguments introduced"""
        # Extract key phrases from current turn
        current_phrases = set(re.findall(r'\b\w{4,}\b', turn.message.lower()))
        
        # Extract phrases from history
        historical_phrases = set()
        for h_turn in history:
            historical_phrases.update(re.findall(r'\b\w{4,}\b', h_turn.message.lower()))
        
        # New phrases indicate new arguments
        new_phrases = current_phrases - historical_phrases
        return len(new_phrases) // 3  # Rough estimate: 3 new words = 1 new argument
    
    def calculate_session_quality(self, session: DebateSession) -> QualityReport:
        """Calculate overall quality report for entire session"""
        if not session.turn_history:
            return QualityReport(
                overall_score=0.0,
                coherence=0.0,
                relevance=0.0,
                engagement=0.0,
                authenticity=0.0,
                alerts=["No turns in session"],
                recommendations=["Start the debate"],
                timestamp=datetime.now()
            )
        
        # Calculate metrics for all turns
        all_metrics = []
        for turn in session.turn_history:
            metrics = self.calculate_turn_metrics(turn, session, session.topic)
            all_metrics.append(metrics)
        
        # Aggregate scores
        coherence = statistics.mean([m.coherence_score for m in all_metrics])
        relevance = statistics.mean([m.relevance_score for m in all_metrics])
        diversity = statistics.mean([m.diversity_score for m in all_metrics])
        authenticity = statistics.mean([m.authenticity_score for m in all_metrics])
        
        # Engagement combines diversity and reference patterns
        engagement = (diversity + min(sum(m.reference_count for m in all_metrics) / len(all_metrics) * 0.2, 1.0)) / 2
        
        # Overall score
        overall = (coherence + relevance + engagement + authenticity) / 4
        
        # Generate alerts
        alerts = []
        if coherence < self.ALERT_THRESHOLDS['coherence_drop']:
            alerts.append(f"Low coherence: {coherence:.1%}")
        if relevance < self.ALERT_THRESHOLDS['topic_drift']:
            alerts.append(f"Topic drift detected: {relevance:.1%}")
        if diversity < self.ALERT_THRESHOLDS['repetition']:
            alerts.append(f"High repetition: {diversity:.1%}")
        if authenticity < self.ALERT_THRESHOLDS['fake_detection']:
            alerts.append(f"Authenticity concern: {authenticity:.1%}")
        
        # Generate recommendations
        recommendations = []
        if coherence < 0.7:
            recommendations.append("Encourage agents to reference previous points")
        if relevance < 0.7:
            recommendations.append("Steer conversation back to main topic")
        if engagement < 0.7:
            recommendations.append("Introduce new perspectives or challenges")
        if authenticity < 0.7:
            recommendations.append("Check API connectivity and response patterns")
        
        return QualityReport(
            overall_score=overall,
            coherence=coherence,
            relevance=relevance,
            engagement=engagement,
            authenticity=authenticity,
            alerts=alerts,
            recommendations=recommendations,
            timestamp=datetime.now()
        )