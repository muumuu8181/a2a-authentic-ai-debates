"""
Checkpoint Manager - Session State Persistence
=============================================

Manages checkpoints for debate sessions based on Luna's design.
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict
import uuid
from enum import Enum

from .session_manager import DebateSession, SessionStatus, DiscussionTurn


class CheckpointType(Enum):
    """Types of checkpoints"""
    AUTOMATIC = "automatic"      # After each turn
    MANUAL = "manual"           # User-triggered
    SCHEDULED = "scheduled"     # Time-based
    EMERGENCY = "emergency"     # Error recovery


@dataclass
class AgentState:
    """State of an individual agent at checkpoint"""
    agent_id: str
    last_response: str
    response_time: float
    turn_count: int
    personality_params: Dict[str, Any]
    conversation_summary: str = ""


@dataclass
class SessionCheckpoint:
    """Complete checkpoint of a debate session"""
    checkpoint_id: str
    session_id: str
    timestamp: datetime
    turn_number: int
    checkpoint_type: CheckpointType
    status: SessionStatus
    participants_state: Dict[str, AgentState]
    quality_snapshot: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def validate(self) -> bool:
        """Verify checkpoint integrity"""
        # Check required fields
        if not all([self.checkpoint_id, self.session_id, self.timestamp]):
            return False
        
        # Verify participant states
        if not self.participants_state:
            return False
        
        # Check turn number consistency
        if self.turn_number < 0:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['checkpoint_type'] = self.checkpoint_type.value
        data['status'] = self.status.value
        
        # Convert agent states
        data['participants_state'] = {
            agent_id: asdict(state) 
            for agent_id, state in self.participants_state.items()
        }
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionCheckpoint':
        """Create from dictionary"""
        # Convert timestamp
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        # Convert enums
        data['checkpoint_type'] = CheckpointType(data['checkpoint_type'])
        data['status'] = SessionStatus(data['status'])
        
        # Convert agent states
        data['participants_state'] = {
            agent_id: AgentState(**state_data)
            for agent_id, state_data in data['participants_state'].items()
        }
        
        return cls(**data)


class CheckpointManager:
    """Manages session checkpoints for recovery and analysis"""
    
    def __init__(self, checkpoint_dir: str = "discussions/checkpoints"):
        self.checkpoint_dir = checkpoint_dir
        self._ensure_directory()
        
        # Configuration
        self.auto_checkpoint_enabled = True
        self.checkpoint_every_n_turns = 1  # Every turn by default
        self.include_quality_snapshot = True  # Luna's recommendation
        
    def _ensure_directory(self):
        """Ensure checkpoint directory exists"""
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        # Create subdirectories for organization
        for subdir in ['automatic', 'manual', 'scheduled', 'emergency']:
            os.makedirs(os.path.join(self.checkpoint_dir, subdir), exist_ok=True)
    
    def create_checkpoint(
        self,
        session: DebateSession,
        checkpoint_type: CheckpointType = CheckpointType.AUTOMATIC,
        quality_snapshot: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SessionCheckpoint:
        """Create a new checkpoint from current session state"""
        
        # Extract participant states
        participants_state = {}
        
        # Group turns by agent
        agent_turns = {}
        for turn in session.turn_history:
            if turn.agent_id not in agent_turns:
                agent_turns[turn.agent_id] = []
            agent_turns[turn.agent_id].append(turn)
        
        # Create agent states
        for participant in session.participants:
            agent_id = participant['id']
            agent_name = participant['name']
            
            # Get agent's turns
            turns = agent_turns.get(agent_id, [])
            
            if turns:
                last_turn = turns[-1]
                last_response = last_turn.message
                last_response_time = last_turn.response_time
            else:
                last_response = ""
                last_response_time = 0.0
            
            # Create agent state
            agent_state = AgentState(
                agent_id=agent_id,
                last_response=last_response,
                response_time=last_response_time,
                turn_count=len(turns),
                personality_params={
                    "name": agent_name,
                    "role": participant.get('role', 'unknown')
                },
                conversation_summary=self._generate_summary(turns)
            )
            
            participants_state[agent_id] = agent_state
        
        # Create checkpoint
        checkpoint = SessionCheckpoint(
            checkpoint_id=str(uuid.uuid4()),
            session_id=session.session_id,
            timestamp=datetime.now(),
            turn_number=session.current_turn,
            checkpoint_type=checkpoint_type,
            status=session.status,
            participants_state=participants_state,
            quality_snapshot=quality_snapshot,
            metadata=metadata or {}
        )
        
        # Validate before saving
        if not checkpoint.validate():
            raise ValueError("Invalid checkpoint data")
        
        # Save checkpoint
        self.save_checkpoint(checkpoint)
        
        return checkpoint
    
    def save_checkpoint(self, checkpoint: SessionCheckpoint):
        """Save checkpoint to disk"""
        # Determine subdirectory based on type
        subdir = checkpoint.checkpoint_type.value
        
        # Create filename
        filename = f"{checkpoint.session_id}_{checkpoint.checkpoint_id}.json"
        filepath = os.path.join(self.checkpoint_dir, subdir, filename)
        
        # Save as JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(checkpoint.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[SessionCheckpoint]:
        """Load checkpoint by ID"""
        # Search in all subdirectories
        for subdir in ['automatic', 'manual', 'scheduled', 'emergency']:
            dir_path = os.path.join(self.checkpoint_dir, subdir)
            
            for filename in os.listdir(dir_path):
                if checkpoint_id in filename:
                    filepath = os.path.join(dir_path, filename)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    return SessionCheckpoint.from_dict(data)
        
        return None
    
    def get_session_checkpoints(
        self, 
        session_id: str,
        checkpoint_type: Optional[CheckpointType] = None
    ) -> List[SessionCheckpoint]:
        """Get all checkpoints for a session"""
        checkpoints = []
        
        # Determine which directories to search
        if checkpoint_type:
            subdirs = [checkpoint_type.value]
        else:
            subdirs = ['automatic', 'manual', 'scheduled', 'emergency']
        
        for subdir in subdirs:
            dir_path = os.path.join(self.checkpoint_dir, subdir)
            
            for filename in os.listdir(dir_path):
                if session_id in filename:
                    filepath = os.path.join(dir_path, filename)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    checkpoint = SessionCheckpoint.from_dict(data)
                    checkpoints.append(checkpoint)
        
        # Sort by timestamp
        checkpoints.sort(key=lambda c: c.timestamp)
        
        return checkpoints
    
    def get_latest_checkpoint(self, session_id: str) -> Optional[SessionCheckpoint]:
        """Get the most recent checkpoint for a session"""
        checkpoints = self.get_session_checkpoints(session_id)
        
        if checkpoints:
            return checkpoints[-1]
        
        return None
    
    def save_emergency_checkpoint(
        self, 
        session_id: str, 
        error: Exception,
        session: Optional[DebateSession] = None
    ) -> Optional[SessionCheckpoint]:
        """Save emergency checkpoint during error (for Oliver's retry handler)"""
        if not session:
            # Try to recover session from previous checkpoints
            latest = self.get_latest_checkpoint(session_id)
            if not latest:
                return None
            
            # Create minimal session for checkpoint
            # (In real implementation, would reconstruct from checkpoint)
            return latest
        
        # Create emergency checkpoint
        metadata = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "emergency_save": True
        }
        
        checkpoint = self.create_checkpoint(
            session=session,
            checkpoint_type=CheckpointType.EMERGENCY,
            metadata=metadata
        )
        
        return checkpoint
    
    def _generate_summary(self, turns: List[DiscussionTurn]) -> str:
        """Generate brief summary of agent's conversation"""
        if not turns:
            return "No conversation yet"
        
        # Simple summary: first and last key points
        if len(turns) == 1:
            # Extract first 100 chars
            return turns[0].message[:100] + "..."
        else:
            first_point = turns[0].message[:50]
            last_point = turns[-1].message[:50]
            return f"Started: {first_point}... Latest: {last_point}..."
    
    def cleanup_old_checkpoints(self, days_to_keep: int = 7):
        """Remove old checkpoints to save space"""
        import time
        
        current_time = time.time()
        cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)
        
        removed_count = 0
        
        for subdir in ['automatic', 'manual', 'scheduled', 'emergency']:
            dir_path = os.path.join(self.checkpoint_dir, subdir)
            
            for filename in os.listdir(dir_path):
                filepath = os.path.join(dir_path, filename)
                
                # Check file age
                file_time = os.path.getmtime(filepath)
                if file_time < cutoff_time:
                    os.remove(filepath)
                    removed_count += 1
        
        return removed_count