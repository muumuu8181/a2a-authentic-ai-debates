"""
Debate Agent B - Con-Side Debater
=================================

Pre-configured agent that takes the "con" or negative side in debates.
Can use different personality types.
"""

from ..personalities.logical_debater import LogicalDebater
from ..personalities.emotional_debater import EmotionalDebater
from ..personalities.philosophical_debater import PhilosophicalDebater


class DebateAgentB:
    """Factory for creating con-side debate agents with different personalities"""
    
    @staticmethod
    def create_logical(name: str = "Logic Con") -> LogicalDebater:
        """Create a logical con-side debater"""
        return LogicalDebater(
            agent_id="agent_b_logical",
            name=name,
            stance="con"
        )
    
    @staticmethod
    def create_emotional(name: str = "Heart Con") -> EmotionalDebater:
        """Create an emotional con-side debater"""
        return EmotionalDebater(
            agent_id="agent_b_emotional", 
            name=name,
            stance="con"
        )
    
    @staticmethod
    def create_philosophical(name: str = "Wisdom Con") -> PhilosophicalDebater:
        """Create a philosophical con-side debater"""
        return PhilosophicalDebater(
            agent_id="agent_b_philosophical",
            name=name,
            stance="con"
        )
    
    @staticmethod
    def create_default(personality: str = "logical", name: str = None) -> any:
        """Create default con-side agent with specified personality"""
        if name is None:
            name = f"{personality.title()} Con"
        
        if personality == "logical":
            return DebateAgentB.create_logical(name)
        elif personality == "emotional":
            return DebateAgentB.create_emotional(name)
        elif personality == "philosophical":
            return DebateAgentB.create_philosophical(name)
        else:
            raise ValueError(f"Unknown personality type: {personality}")