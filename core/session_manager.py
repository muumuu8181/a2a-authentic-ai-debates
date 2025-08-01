"""
Session Manager - Multi-Round Discussion Management
==================================================

Manages complex multi-round AI discussions and debates.
Handles state persistence, turn management, and conversation flow.
"""

from typing import Dict, List, Optional, Any
import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import uuid


class SessionStatus(Enum):
    """Session status enumeration"""
    PENDING = "pending"
    ACTIVE = "active" 
    COMPLETED = "completed"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class DiscussionTurn:
    """Represents one turn in a discussion"""
    turn_number: int
    agent_id: str
    agent_name: str
    message: str
    timestamp: str
    response_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass  
class DebateSession:
    """Manages a complete debate session between AI agents"""
    
    session_id: str
    topic: str
    participants: List[Dict[str, str]]  # [{"id": "agent1", "name": "Pro Agent", "role": "pro"}]
    status: SessionStatus
    created_at: str
    updated_at: str
    turn_history: List[DiscussionTurn]
    current_turn: int = 0
    max_turns: int = 10
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SessionManager:
    """Manages debate sessions and discussion state"""
    
    def __init__(self, discussions_path: str = "discussions"):
        self.discussions_path = discussions_path
        self.active_sessions: Dict[str, DebateSession] = {}
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure discussion directories exist"""
        for subdir in ["sessions", "completed", "scenarios", "logs"]:
            os.makedirs(os.path.join(self.discussions_path, subdir), exist_ok=True)
    
    def create_session(self, topic: str, participants: List[Dict[str, str]], 
                      max_turns: int = 10) -> DebateSession:
        """Create a new debate session"""
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        session = DebateSession(
            session_id=session_id,
            topic=topic,
            participants=participants,
            status=SessionStatus.PENDING,
            created_at=now,
            updated_at=now,
            turn_history=[],
            current_turn=0,
            max_turns=max_turns
        )
        
        self.active_sessions[session_id] = session
        self.save_session(session)
        return session
    
    def add_turn(self, session_id: str, agent_id: str, agent_name: str, 
                message: str, response_time: float = 0.0) -> bool:
        """Add a new turn to the session"""
        if session_id not in self.active_sessions:
            return False
            
        session = self.active_sessions[session_id]
        
        if session.status != SessionStatus.ACTIVE:
            if session.status == SessionStatus.PENDING:
                session.status = SessionStatus.ACTIVE
            else:
                return False
        
        turn = DiscussionTurn(
            turn_number=session.current_turn + 1,
            agent_id=agent_id,
            agent_name=agent_name,
            message=message,
            timestamp=datetime.now().isoformat(),
            response_time=response_time
        )
        
        session.turn_history.append(turn)
        session.current_turn += 1
        session.updated_at = datetime.now().isoformat()
        
        # Check if session should be completed
        if session.current_turn >= session.max_turns:
            session.status = SessionStatus.COMPLETED
            self.complete_session(session_id)
        
        self.save_session(session)
        return True
    
    def get_session(self, session_id: str) -> Optional[DebateSession]:
        """Get session by ID"""
        return self.active_sessions.get(session_id)
    
    def save_session(self, session: DebateSession):
        """Save session to disk"""
        if session.status == SessionStatus.COMPLETED:
            filepath = os.path.join(self.discussions_path, "completed", f"{session.session_id}.json")
        else:
            filepath = os.path.join(self.discussions_path, "sessions", f"{session.session_id}.json")
        
        # Convert to dict and handle enum serialization
        session_dict = asdict(session)
        session_dict['status'] = session.status.value
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_dict, f, indent=2, ensure_ascii=False)
    
    def complete_session(self, session_id: str) -> bool:
        """Complete a session and move to completed folder"""
        if session_id not in self.active_sessions:
            return False
            
        session = self.active_sessions[session_id]
        session.status = SessionStatus.COMPLETED
        session.updated_at = datetime.now().isoformat()
        
        # Move from sessions to completed
        old_path = os.path.join(self.discussions_path, "sessions", f"{session_id}.json")
        if os.path.exists(old_path):
            os.remove(old_path)
        
        self.save_session(session)
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        return True
    
    def load_session(self, session_id: str) -> Optional[DebateSession]:
        """Load session from disk"""
        # Try active sessions first
        filepath = os.path.join(self.discussions_path, "sessions", f"{session_id}.json")
        if not os.path.exists(filepath):
            # Try completed sessions
            filepath = os.path.join(self.discussions_path, "completed", f"{session_id}.json")
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert status back to enum
            data['status'] = SessionStatus(data['status'])
            
            # Convert turn history
            turns = []
            for turn_data in data['turn_history']:
                turns.append(DiscussionTurn(**turn_data))
            data['turn_history'] = turns
            
            session = DebateSession(**data)
            
            if session.status in [SessionStatus.ACTIVE, SessionStatus.PENDING]:
                self.active_sessions[session_id] = session
            
            return session
            
        except (json.JSONDecodeError, KeyError, ValueError):
            return None
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of the session"""
        session = self.get_session(session_id) or self.load_session(session_id)
        if not session:
            return None
        
        return {
            "session_id": session.session_id,
            "topic": session.topic,
            "status": session.status.value,
            "participants": session.participants,
            "turn_count": len(session.turn_history),
            "max_turns": session.max_turns,
            "created_at": session.created_at,
            "updated_at": session.updated_at
        }