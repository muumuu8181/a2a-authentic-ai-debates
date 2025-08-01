"""
Base Agent Class - Foundation for All Debate Agents
===================================================

Provides common functionality for all AI debate agents.
"""

import subprocess
import os
import time
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.error_handler import retry_with_backoff, RetryConfig, error_logger

logger = logging.getLogger(__name__)


class BaseDebateAgent(ABC):
    """Base class for all debate agents"""
    
    def __init__(self, agent_id: str, name: str, role: str, personality_type: str):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.personality_type = personality_type
        self.conversation_history = []
        
        # Gemini CLI configuration
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY環境変数が設定されていません")
        
        # Path to Gemini CLI (assuming it's in parent directory)
        self.gemini_cli_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            "gemini-cli.js"
        )
        
        logger.info(f"✅ {self.name} ({self.personality_type}) 初期化完了")
    
    @abstractmethod
    def get_system_prompt(self, topic: str, context: str = "") -> str:
        """Generate system prompt based on personality and context"""
        pass
    
    async def generate_response(self, topic: str, opponent_message: str = "", 
                              context: str = "", turn_number: int = 1) -> str:
        """Generate debate response using Gemini CLI"""
        
        # Build the full prompt
        system_prompt = self.get_system_prompt(topic, context)
        
        if opponent_message:
            full_prompt = f"""{system_prompt}

議論のトピック: {topic}

相手の主張: {opponent_message}

あなたのターン {turn_number} です。相手の主張に対して、あなたの立場から応答してください。
論理的で説得力のある議論を展開してください。"""
        else:
            full_prompt = f"""{system_prompt}

議論のトピック: {topic}

これは議論の最初のターンです。あなたの立場から、このトピックについて最初の主張を述べてください。
論理的で説得力のある議論を展開してください。"""
        
        logger.info(f"🤖 {self.name}: 応答生成中...")
        
        try:
            # Execute Gemini CLI with retry logic
            env = os.environ.copy()
            env["GEMINI_API_KEY"] = self.gemini_api_key
            
            # Configure retry for API calls
            api_retry_config = RetryConfig(
                max_attempts=3,
                initial_delay=2.0,
                max_delay=30.0,
                exponential_base=2.0
            )
            
            @retry_with_backoff(
                config=api_retry_config,
                exceptions=(subprocess.TimeoutExpired, subprocess.CalledProcessError),
                on_retry=lambda e, attempt: logger.warning(
                    f"{self.name}: Retry attempt {attempt} after error: {str(e)}"
                )
            )
            def call_gemini_cli():
                start_time = time.time()
                result = subprocess.run(
                    ["node", self.gemini_cli_path, full_prompt],
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=60  # Increased timeout from 30s to 60s
                )
                end_time = time.time()
                
                if result.returncode != 0:
                    error_msg = result.stderr or "Unknown error"
                    raise subprocess.CalledProcessError(
                        result.returncode, 
                        ["node", self.gemini_cli_path], 
                        output=result.stdout,
                        stderr=error_msg
                    )
                
                return result, end_time - start_time
            
            # Call with retry logic
            result, response_time = call_gemini_cli()
            
            # Extract AI response (remove debug output)
            output_lines = result.stdout.strip().split('\n')
            ai_response = ""
            found_separator = False
            
            for line in output_lines:
                if "===" in line and "検索中" in line:
                    found_separator = True
                    continue
                if found_separator:
                    ai_response += line + "\n"
            
            ai_response = ai_response.strip()
            if not ai_response:
                ai_response = result.stdout.strip()
            
            # Store in conversation history
            self.conversation_history.append({
                "turn": turn_number,
                "topic": topic,
                "opponent_message": opponent_message,
                "response": ai_response,
                "response_time": response_time,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            })
            
            logger.info(f"✅ {self.name}: 応答生成完了 ({response_time:.2f}秒)")
            return ai_response
                
        except Exception as e:
            # Log error with full context
            error_context = {
                "agent_name": self.name,
                "turn_number": turn_number,
                "topic": topic,
                "error_type": type(e).__name__
            }
            
            user_message = error_logger.log_error(
                e, 
                context=error_context,
                user_message=f"{self.name}: 応答生成中にエラーが発生しました。"
            )
            
            return user_message
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "personality_type": self.personality_type,
            "conversation_history_length": len(self.conversation_history)
        }