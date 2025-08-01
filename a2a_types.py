"""A2A Protocol Types - 簡易実装"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class Role(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class TextPart(BaseModel):
    text: str
    type: str = "text"


class Part(BaseModel):
    root: TextPart


class Message(BaseModel):
    role: Role
    parts: List[Part]


class AgentSkill(BaseModel):
    id: str
    name: str
    description: str
    tags: List[str] = []
    examples: List[str] = []


class AgentCapabilities(BaseModel):
    streaming: bool = False
    pushNotifications: bool = False


class AgentAuthentication(BaseModel):
    schemes: List[str] = []


class AgentCard(BaseModel):
    name: str
    description: str
    url: str
    version: str = "1.0.0"
    defaultInputModes: List[str] = ["text"]
    defaultOutputModes: List[str] = ["text"]
    capabilities: AgentCapabilities = Field(default_factory=AgentCapabilities)
    authentication: AgentAuthentication = Field(default_factory=AgentAuthentication)
    skills: List[AgentSkill] = []


class TaskStatus(str, Enum):
    PENDING = "pending"
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseModel):
    id: str
    status: TaskStatus
    message: Optional[Message] = None
    result: Optional[Message] = None
    error: Optional[str] = None