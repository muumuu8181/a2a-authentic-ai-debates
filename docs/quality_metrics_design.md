# AI Debate Quality Metrics Design

**Author**: Luna (Technical Reviewer)  
**Date**: 2025-08-01  
**Version**: 1.0  
**Status**: Draft

---

## 📊 Executive Summary

This document defines comprehensive quality metrics for evaluating AI-to-AI debates, ensuring meaningful conversations that meet Boss's vision of genuine, engaging AI discussions.

## 🎯 Core Objectives

1. **Measure Conversation Quality**: Not just response generation, but meaningful dialogue
2. **Prevent Fake Discussions**: Detect scripted or repetitive patterns
3. **Ensure Engagement**: Track how compelling the debates are
4. **Guide Improvements**: Provide actionable feedback for system enhancement

## 📐 Metric Categories

### 1. Coherence Metrics (議論の一貫性)

#### 1.1 Context Retention Score (CRS)
```python
def calculate_context_retention(turn: DiscussionTurn, history: List[DiscussionTurn]) -> float:
    """
    Measures how well an agent remembers and references previous points
    Score: 0.0 (no context) to 1.0 (perfect retention)
    """
    references_found = count_previous_references(turn, history)
    expected_references = calculate_expected_references(turn.turn_number)
    return min(references_found / expected_references, 1.0)
```

#### 1.2 Argument Progression Index (API)
```python
def calculate_argument_progression(session: DebateSession) -> float:
    """
    Tracks whether arguments evolve or just repeat
    Score: 0.0 (circular) to 1.0 (constantly evolving)
    """
    unique_points = extract_unique_arguments(session.turn_history)
    total_points = count_all_arguments(session.turn_history)
    return unique_points / total_points
```

### 2. Relevance Metrics (トピック関連性)

#### 2.1 Topic Adherence Score (TAS)
```python
def calculate_topic_adherence(turn: DiscussionTurn, topic: str) -> float:
    """
    Measures how closely responses relate to the debate topic
    Uses semantic similarity between response and topic
    """
    topic_embedding = get_embedding(topic)
    response_embedding = get_embedding(turn.message)
    return cosine_similarity(topic_embedding, response_embedding)
```

#### 2.2 Drift Detection Ratio (DDR)
```python
def detect_topic_drift(session: DebateSession) -> DriftAnalysis:
    """
    Identifies when and how conversations drift from topic
    """
    drift_points = []
    for i, turn in enumerate(session.turn_history[1:]):
        drift_score = 1.0 - calculate_topic_adherence(turn, session.topic)
        if drift_score > DRIFT_THRESHOLD:
            drift_points.append(DriftPoint(turn_number=i+1, score=drift_score))
    return DriftAnalysis(drift_points, calculate_recovery_rate(drift_points))
```

### 3. Engagement Metrics (対話の魅力度)

#### 3.1 Response Diversity Index (RDI)
```python
def calculate_response_diversity(agent_turns: List[DiscussionTurn]) -> float:
    """
    Prevents repetitive responses, ensures variety
    """
    vocabulary_richness = calculate_vocabulary_variety(agent_turns)
    structure_variety = calculate_sentence_structure_variety(agent_turns)
    argument_variety = calculate_argument_type_variety(agent_turns)
    
    return weighted_average([
        (vocabulary_richness, 0.3),
        (structure_variety, 0.3),
        (argument_variety, 0.4)
    ])
```

#### 3.2 Debate Intensity Score (DIS)
```python
def calculate_debate_intensity(session: DebateSession) -> float:
    """
    Measures how actively agents challenge each other
    """
    challenges = count_counterarguments(session)
    agreements = count_agreements(session)
    new_perspectives = count_new_perspectives(session)
    
    return normalize_score(challenges * 2 + new_perspectives - agreements * 0.5)
```

### 4. Authenticity Metrics (真正性の検証)

#### 4.1 Response Time Variance (RTV)
```python
def analyze_response_times(session: DebateSession) -> AuthenticityScore:
    """
    Real AI calls have variable response times
    Fake demos often have consistent timing
    """
    times = [turn.response_time for turn in session.turn_history]
    variance = calculate_variance(times)
    expected_variance = get_expected_variance_range()
    
    if variance < expected_variance.min:
        return AuthenticityScore(score=0.3, reason="Suspiciously consistent timing")
    elif variance > expected_variance.max:
        return AuthenticityScore(score=0.7, reason="Unusual variance in timing")
    else:
        return AuthenticityScore(score=1.0, reason="Natural response time variation")
```

#### 4.2 Linguistic Fingerprint Analysis (LFA)
```python
def analyze_linguistic_fingerprint(agent_turns: List[DiscussionTurn]) -> float:
    """
    Each AI should have subtle stylistic differences
    Identical patterns suggest scripting
    """
    fingerprints = []
    for turn in agent_turns:
        fingerprint = extract_linguistic_features(turn.message)
        fingerprints.append(fingerprint)
    
    diversity_score = calculate_fingerprint_diversity(fingerprints)
    consistency_score = calculate_agent_consistency(fingerprints)
    
    return balance_scores(diversity_score, consistency_score)
```

### 5. Technical Quality Metrics

#### 5.1 API Success Rate
```python
success_rate = successful_api_calls / total_api_calls
```

#### 5.2 Error Recovery Rate
```python
recovery_rate = successful_recoveries / total_errors
```

#### 5.3 Session Completion Rate
```python
completion_rate = completed_sessions / total_sessions
```

## 📈 Composite Quality Score

### Overall Debate Quality (ODQ)
```python
def calculate_overall_quality(session: DebateSession) -> QualityReport:
    """
    Combines all metrics into a comprehensive score
    """
    scores = {
        'coherence': calculate_coherence_score(session),      # 25%
        'relevance': calculate_relevance_score(session),      # 25%
        'engagement': calculate_engagement_score(session),     # 25%
        'authenticity': calculate_authenticity_score(session), # 25%
    }
    
    overall = weighted_average([
        (scores['coherence'], 0.25),
        (scores['relevance'], 0.25),
        (scores['engagement'], 0.25),
        (scores['authenticity'], 0.25)
    ])
    
    return QualityReport(
        overall_score=overall,
        component_scores=scores,
        recommendations=generate_recommendations(scores),
        timestamp=datetime.now()
    )
```

## 🎨 Visualization Dashboard

### Real-time Metrics Display
```
┌─────────────────────────────────────────────────┐
│           AI Debate Quality Dashboard            │
├─────────────────────────────────────────────────┤
│ Overall Quality: ████████░░ 83%                 │
├─────────────────────────────────────────────────┤
│ Coherence    [████████░░] 85%  ↑2%             │
│ Relevance    [███████░░░] 78%  ↓5%             │
│ Engagement   [█████████░] 92%  ↑8%             │
│ Authenticity [████████░░] 80%  →0%             │
├─────────────────────────────────────────────────┤
│ Current Turn: 15/20  |  Duration: 00:12:34      │
│ Drift Events: 2      |  Recoveries: 2           │
└─────────────────────────────────────────────────┘
```

### Historical Trends
- Quality over time graphs
- Per-agent performance tracking
- Topic-specific success rates
- Peak engagement moments

## 🔔 Alert Thresholds

### Quality Alerts
```python
ALERT_THRESHOLDS = {
    'coherence_drop': 0.6,      # Alert if coherence < 60%
    'topic_drift': 0.7,         # Alert if drift > 70%
    'repetition': 0.5,          # Alert if diversity < 50%
    'fake_detection': 0.4,      # Alert if authenticity < 40%
}
```

### Automatic Interventions
- **Low Coherence**: Inject context reminder
- **Topic Drift**: Gentle redirection prompt
- **High Repetition**: Personality adjustment
- **Fake Pattern**: System health check

## 📊 Data Collection

### Per-Turn Metrics
```python
@dataclass
class TurnMetrics:
    turn_id: str
    timestamp: datetime
    response_time: float
    coherence_score: float
    relevance_score: float
    diversity_contribution: float
    reference_count: int
    new_arguments: int
    linguistic_features: Dict[str, float]
```

### Session Summary
```python
@dataclass
class SessionMetrics:
    session_id: str
    overall_quality: float
    component_scores: Dict[str, float]
    turn_metrics: List[TurnMetrics]
    alerts_triggered: List[QualityAlert]
    recommendations: List[str]
```

## 🧪 Validation & Calibration

### Human Evaluation Correlation
- Regular human rating sessions
- Metric calibration based on feedback
- A/B testing of threshold values

### Continuous Improvement
```python
class MetricCalibrator:
    def collect_human_feedback(self, session_id: str, rating: HumanRating):
        """Store human evaluation for calibration"""
        
    def calibrate_weights(self) -> WeightAdjustment:
        """Adjust metric weights based on human correlation"""
        
    def validate_thresholds(self) -> ThresholdReport:
        """Ensure alerts match human perception"""
```

## 🔌 Integration Points

### With Session Manager
- Real-time metric calculation
- Quality-based session control
- Checkpoint quality scores

### With Agent System
- Personality adjustments based on metrics
- Dynamic prompt modifications
- Performance feedback loops

### With Logging System
- Structured metric logging
- Searchable quality history
- Anomaly detection

## 📈 Success Criteria

1. **Accuracy**: 85%+ correlation with human quality assessment
2. **Real-time**: All metrics calculated within 100ms
3. **Actionable**: 90%+ of alerts lead to quality improvement
4. **Scalable**: Support 10+ concurrent session monitoring

## 🚀 Implementation Roadmap

### Phase 1: Core Metrics (Week 2)
- Implement coherence & relevance scores
- Basic dashboard visualization
- Integration with session manager

### Phase 2: Advanced Analytics (Week 3)
- Engagement & authenticity metrics
- Alert system implementation
- Historical analysis tools

### Phase 3: Optimization (Post-launch)
- Machine learning enhancements
- Predictive quality modeling
- Automated calibration

---

**Next Steps**: Review with Oliver, prioritize metrics for Week 2 implementation