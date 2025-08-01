# Dynamic Personality System Design

**Author**: Luna (Technical Reviewer)  
**Date**: 2025-08-01  
**Version**: 1.0  
**Status**: Draft

---

## 🎭 Executive Summary

This document specifies a dynamic personality system that allows AI agents to adjust their debate styles during discussions, creating more engaging and realistic conversations.

## 🎯 Design Philosophy

**Static personalities are predictable. Dynamic personalities are engaging.**

Our system enables:
- Mid-debate personality shifts based on conversation flow
- Emotional response to opponent's arguments  
- Strategic style changes to strengthen positions
- Natural personality evolution throughout debates

## 🧬 Personality Model

### Core Personality Traits
```python
@dataclass
class PersonalityTraits:
    # Debate Style (0.0 - 1.0)
    logical_analytical: float      # Data-driven vs Intuitive
    emotional_expressive: float    # Passionate vs Reserved  
    philosophical_depth: float     # Abstract vs Concrete
    
    # Communication Style (0.0 - 1.0)
    assertiveness: float          # Aggressive vs Passive
    formality: float             # Formal vs Casual
    empathy: float               # Understanding vs Dismissive
    
    # Behavioral Traits (0.0 - 1.0)
    flexibility: float           # Adaptable vs Rigid
    creativity: float            # Novel vs Traditional
    skepticism: float            # Questioning vs Accepting
```

### Personality Profiles
```python
PERSONALITY_PRESETS = {
    "logical_debater": PersonalityTraits(
        logical_analytical=0.9,
        emotional_expressive=0.2,
        philosophical_depth=0.5,
        assertiveness=0.7,
        formality=0.8,
        empathy=0.4,
        flexibility=0.3,
        creativity=0.4,
        skepticism=0.8
    ),
    
    "emotional_advocate": PersonalityTraits(
        logical_analytical=0.3,
        emotional_expressive=0.9,
        philosophical_depth=0.6,
        assertiveness=0.8,
        formality=0.4,
        empathy=0.9,
        flexibility=0.7,
        creativity=0.8,
        skepticism=0.3
    ),
    
    "philosophical_thinker": PersonalityTraits(
        logical_analytical=0.6,
        emotional_expressive=0.5,
        philosophical_depth=0.9,
        assertiveness=0.5,
        formality=0.7,
        empathy=0.7,
        flexibility=0.8,
        creativity=0.9,
        skepticism=0.6
    )
}
```

## 🔄 Dynamic Adjustment System

### Adjustment Triggers
```python
class PersonalityTrigger(Enum):
    LOSING_ARGUMENT = "losing_argument"          # Increase assertiveness
    WINNING_ARGUMENT = "winning_argument"        # Decrease aggression
    OPPONENT_EMOTIONAL = "opponent_emotional"    # Increase empathy
    OPPONENT_LOGICAL = "opponent_logical"        # Increase analytical
    TOPIC_SHIFT = "topic_shift"                # Adjust relevance
    STALEMATE = "stalemate"                    # Increase creativity
    HIGH_TENSION = "high_tension"              # Modulate calmness
```

### Adjustment Algorithm
```python
class PersonalityAdjuster:
    def __init__(self, base_personality: PersonalityTraits):
        self.base = base_personality
        self.current = deepcopy(base_personality)
        self.history = []
        
    def adjust(self, trigger: PersonalityTrigger, intensity: float = 0.1):
        """
        Adjust personality based on trigger
        intensity: 0.0-1.0 (how much to adjust)
        """
        adjustments = self.get_adjustments(trigger)
        
        for trait, delta in adjustments.items():
            current_value = getattr(self.current, trait)
            new_value = self.clamp(current_value + (delta * intensity))
            setattr(self.current, trait, new_value)
            
        self.history.append(PersonalitySnapshot(
            timestamp=datetime.now(),
            trigger=trigger,
            traits=deepcopy(self.current)
        ))
    
    def get_adjustments(self, trigger: PersonalityTrigger) -> Dict[str, float]:
        """Define how each trigger affects traits"""
        adjustments = {
            PersonalityTrigger.LOSING_ARGUMENT: {
                "assertiveness": +0.2,
                "logical_analytical": +0.1,
                "creativity": +0.15
            },
            PersonalityTrigger.OPPONENT_EMOTIONAL: {
                "empathy": +0.2,
                "emotional_expressive": +0.1,
                "formality": -0.1
            },
            # ... more trigger definitions
        }
        return adjustments.get(trigger, {})
```

## 🎨 Personality Expression

### Language Style Modulation
```python
def apply_personality_to_prompt(
    base_prompt: str, 
    personality: PersonalityTraits
) -> str:
    """
    Modify prompt based on current personality
    """
    modifiers = []
    
    # Logical vs Emotional
    if personality.logical_analytical > 0.7:
        modifiers.append("Use data, statistics, and logical reasoning.")
    elif personality.emotional_expressive > 0.7:
        modifiers.append("Appeal to emotions and personal experiences.")
    
    # Formality
    if personality.formality > 0.7:
        modifiers.append("Maintain formal, professional language.")
    elif personality.formality < 0.3:
        modifiers.append("Use conversational, casual tone.")
    
    # Assertiveness
    if personality.assertiveness > 0.8:
        modifiers.append("Be direct and confident in assertions.")
    elif personality.assertiveness < 0.3:
        modifiers.append("Use tentative language and questions.")
    
    enhanced_prompt = f"{base_prompt}\n\nStyle guidelines:\n"
    enhanced_prompt += "\n".join(f"- {mod}" for mod in modifiers)
    
    return enhanced_prompt
```

### Response Filtering
```python
class PersonalityFilter:
    """Post-process AI responses to match personality"""
    
    def filter_response(
        self, 
        raw_response: str, 
        personality: PersonalityTraits
    ) -> str:
        response = raw_response
        
        # Adjust assertiveness
        if personality.assertiveness < 0.3:
            response = self.soften_assertions(response)
        elif personality.assertiveness > 0.8:
            response = self.strengthen_assertions(response)
        
        # Adjust formality
        if personality.formality < 0.3:
            response = self.make_casual(response)
        elif personality.formality > 0.8:
            response = self.make_formal(response)
        
        return response
```

## 📊 Personality Evolution

### Round-based Evolution
```python
class PersonalityEvolution:
    """Manage personality changes across debate rounds"""
    
    def __init__(self, agent_id: str, base_personality: str):
        self.agent_id = agent_id
        self.adjuster = PersonalityAdjuster(
            PERSONALITY_PRESETS[base_personality]
        )
        self.round_strategies = []
    
    def plan_evolution(self, total_rounds: int):
        """Plan personality progression for entire debate"""
        if total_rounds <= 3:
            # Short debate: minimal changes
            self.round_strategies = [
                RoundStrategy(maintain=True),
                RoundStrategy(intensify=True),
                RoundStrategy(maintain=True)
            ]
        else:
            # Longer debate: more complex evolution
            self.round_strategies = self.generate_complex_strategy(total_rounds)
    
    def execute_round(self, round_num: int, opponent_analysis: Dict):
        """Adjust personality for current round"""
        strategy = self.round_strategies[round_num - 1]
        
        # Reactive adjustments based on opponent
        if opponent_analysis['aggression'] > 0.7:
            self.adjuster.adjust(PersonalityTrigger.HIGH_TENSION, 0.2)
        
        # Planned adjustments
        if strategy.intensify:
            self.intensify_core_traits()
        elif strategy.shift:
            self.shift_strategy(strategy.target_style)
```

## 🔧 Integration API

### Simple API for Agents
```python
class DynamicPersonalityAgent:
    def __init__(self, base_personality: str):
        self.personality_system = PersonalityEvolution(
            agent_id=self.agent_id,
            base_personality=base_personality
        )
    
    async def get_response(self, opponent_message: str, round_num: int):
        # Analyze opponent
        opponent_analysis = self.analyze_opponent(opponent_message)
        
        # Adjust personality
        self.personality_system.execute_round(round_num, opponent_analysis)
        
        # Get current personality
        current_traits = self.personality_system.adjuster.current
        
        # Generate response with personality
        prompt = self.build_prompt(opponent_message)
        enhanced_prompt = apply_personality_to_prompt(prompt, current_traits)
        
        raw_response = await self.call_ai(enhanced_prompt)
        final_response = self.personality_filter.filter_response(
            raw_response, 
            current_traits
        )
        
        return final_response
```

### Configuration Options
```yaml
personality_config:
  base_profile: "logical_debater"
  evolution_enabled: true
  adjustment_sensitivity: 0.15  # How quickly to adjust
  revert_to_base_rate: 0.05    # How quickly to return to base
  
  triggers:
    enable_reactive: true       # React to opponent
    enable_strategic: true      # Follow round strategy
    enable_random: false        # Random variations
  
  constraints:
    max_deviation: 0.4         # Max distance from base
    min_consistency: 0.6       # Maintain character
```

## 📈 Monitoring & Analytics

### Personality Tracking
```python
@dataclass
class PersonalityMetrics:
    session_id: str
    agent_id: str
    base_personality: str
    evolution_path: List[PersonalitySnapshot]
    trigger_frequency: Dict[PersonalityTrigger, int]
    trait_variance: Dict[str, float]
    effectiveness_score: float
```

### Visualization
```
Personality Evolution Chart
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Round 1  2  3  4  5  6  7  8  9  10
      
Logic ████████████████▓▓▓▓▓▓▓▓░░░░░░░
Emotion ░░░░▓▓▓▓████████████▓▓▓▓░░░░░░
Assert. ████████████████████████▓▓▓▓░░░░

Triggers: 🔥(High Tension) 💭(Stalemate) 📊(Logic Counter)
```

## 🧪 Testing Strategy

### Unit Tests
- Trait adjustment calculations
- Boundary condition handling
- Personality consistency checks

### Integration Tests  
- Full debate with personality evolution
- Multi-agent personality interactions
- Edge case handling (extreme personalities)

### A/B Testing
- Static vs Dynamic personality effectiveness
- Different evolution strategies
- User engagement metrics

## 🚀 Implementation Phases

### Phase 1: Core System (Week 2)
- Basic trait model
- Simple adjustments
- Manual triggers

### Phase 2: Advanced Features (Week 3)
- Automatic trigger detection
- Complex evolution strategies
- Performance optimization

### Phase 3: Polish (Post-launch)
- Machine learning optimization
- Personality recommendation engine
- Advanced analytics

---

**Next Steps**: Share with Oliver at 15:00, discuss integration priorities