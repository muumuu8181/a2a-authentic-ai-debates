"""
A2A Protocol Handler
===================

Handles core A2A communication protocol functionality.
This is the foundation for all agent-to-agent communication.
"""

from typing import Dict, Any, Optional
import asyncio
import json
from uuid import uuid4
from datetime import datetime

from .a2a_types import Message, Task, TaskStatus, Role


class A2AProtocolHandler:
    """Core A2A protocol communication handler"""
    
    def __init__(self):
        self.active_tasks: Dict[str, Task] = {}
        
    def create_message_request(self, message_text: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a standard A2A message request"""
        if not task_id:
            task_id = str(uuid4())
            
        return {
            "id": str(uuid4()),
            "method": "tasks/send", 
            "params": {
                "taskId": task_id,
                "message": {
                    "role": "user",
                    "parts": [{"text": message_text}]
                }
            }
        }
    
    def parse_response(self, response: Dict[str, Any]) -> Optional[str]:
        """Parse A2A response and extract message text"""
        try:
            if "result" in response and "message" in response["result"]:
                parts = response["result"]["message"]["parts"]
                if parts and len(parts) > 0:
                    return parts[0].get("text", "")
            return None
        except (KeyError, IndexError):
            return None
    
    def create_task(self, task_id: str, user_message: str) -> Task:
        """Create a new task from user message"""
        from .a2a_types import Part, TextPart
        
        task = Task(
            id=task_id,
            status=TaskStatus.WORKING,
            message=Message(
                role=Role.USER,
                parts=[Part(root=TextPart(text=user_message))]
            )
        )
        
        self.active_tasks[task_id] = task
        return task
    
    def complete_task(self, task_id: str, response_text: str) -> Optional[Task]:
        """Complete a task with response"""
        if task_id not in self.active_tasks:
            return None
            
        task = self.active_tasks[task_id]
        from .a2a_types import Part, TextPart
        
        task.status = TaskStatus.COMPLETED
        task.result = Message(
            role=Role.AGENT,
            parts=[Part(root=TextPart(text=response_text))]
        )
        
        return task