"""
Debate Agent A - Pro-Side Debater
=================================

Pre-configured agent that takes the "pro" or affirmative side in debates.
Can use different personality types.
"""

from ..personalities.logical_debater import LogicalDebater
from ..personalities.emotional_debater import EmotionalDebater
from ..personalities.philosophical_debater import PhilosophicalDebater


class DebateAgentA:
    """Factory for creating pro-side debate agents with different personalities"""
    
    @staticmethod
    def create_logical(name: str = "Logic Pro") -> LogicalDebater:
        """Create a logical pro-side debater"""
        return LogicalDebater(
            agent_id="agent_a_logical",
            name=name,
            stance="pro"
        )
    
    @staticmethod
    def create_emotional(name: str = "Heart Pro") -> EmotionalDebater:
        """Create an emotional pro-side debater"""
        return EmotionalDebater(
            agent_id="agent_a_emotional",
            name=name,
            stance="pro"
        )
    
    @staticmethod
    def create_philosophical(name: str = "Wisdom Pro") -> PhilosophicalDebater:
        """Create a philosophical pro-side debater"""
        return PhilosophicalDebater(
            agent_id="agent_a_philosophical",
            name=name,
            stance="pro"
        )
    
    @staticmethod
    def create_default(personality: str = "logical", name: str = None) -> any:
        """Create default pro-side agent with specified personality"""
        if name is None:
            name = f"{personality.title()} Pro"
        
        if personality == "logical":
            return DebateAgentA.create_logical(name)
        elif personality == "emotional":
            return DebateAgentA.create_emotional(name)
        elif personality == "philosophical":
            return DebateAgentA.create_philosophical(name)
        else:
            raise ValueError(f"Unknown personality type: {personality}")