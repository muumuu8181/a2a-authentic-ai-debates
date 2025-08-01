"""A2A AI Agent Server - Gemini搭載の本格的なAIエージェント"""
import asyncio
import json
import logging
import os
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv
import subprocess
import os

from a2a_types import (
    AgentCard, AgentSkill, AgentCapabilities, 
    Message, Part, TextPart, Role, Task, TaskStatus
)

# 環境変数を読み込み
load_dotenv()

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("A2A-AI-Agent")


class GeminiAIAgent:
    """Gemini AIを使用するA2Aエージェント"""
    
    def __init__(self, agent_name: str, agent_role: str):
        self.name = agent_name
        self.role = agent_role
        self.tasks: Dict[str, Task] = {}
        
        # Gemini CLI設定の確認
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY環境変数が設定されていません")
        
        # Gemini CLIのパス（親ディレクトリから相対パス）
        self.gemini_cli_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gemini-cli.js")
        
        # エージェントのシステムプロンプト
        self.system_prompt = f"""あなたは{self.name}という名前のAIエージェントです。
役割: {self.role}
他のAIエージェントと協力して問題を解決します。
簡潔で的確な返答を心がけてください。"""
        
        logger.info(f"✅ {self.name} (Gemini CLI) 初期化完了")
    
    async def process_message(self, message: str) -> str:
        """Gemini CLIを使ってメッセージを処理"""
        logger.info(f"📥 受信メッセージ: '{message}'")
        
        try:
            # プロンプトを作成
            prompt = f"{self.system_prompt}\n\nユーザーからのメッセージ: {message}\n\n返答:"
            
            # Gemini CLIを実行
            env = os.environ.copy()
            env["GEMINI_API_KEY"] = self.gemini_api_key
            
            # コマンドをログに記録
            logger.info(f"🚀 Gemini CLI実行: node {self.gemini_cli_path}")
            logger.info(f"📝 プロンプト長: {len(prompt)} 文字")
            
            result = subprocess.run(
                ["node", self.gemini_cli_path, prompt],
                capture_output=True,
                text=True,
                env=env,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Gemini CLI実行成功")
                logger.info(f"📊 出力サイズ: {len(result.stdout)} 文字")
                
                # 出力から実際のAI応答を抽出（デバッグ情報を除去）
                output_lines = result.stdout.strip().split('\n')
                # "==" を含む行より後の内容を取得
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
                
                logger.info(f"🤖 AI応答（最初の100文字）: '{ai_response[:100]}...'")
                logger.info(f"📏 AI応答長: {len(ai_response)} 文字")
                return ai_response
            else:
                error_msg = result.stderr or "不明なエラー"
                logger.error(f"❌ Gemini CLIエラー: {error_msg}")
                return f"申し訳ありません。エラーが発生しました: {error_msg}"
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Gemini CLI タイムアウト")
            return "申し訳ありません。処理がタイムアウトしました。"
        except Exception as e:
            logger.error(f"❌ Gemini CLI実行エラー: {str(e)}")
            return f"申し訳ありません。エラーが発生しました: {str(e)}"


# コマンドライン引数からエージェント設定を取得
import sys
agent_name = sys.argv[1] if len(sys.argv) > 1 else "研究者エージェント"
agent_role = sys.argv[2] if len(sys.argv) > 2 else "技術的な質問に答える専門家"
port = int(sys.argv[3]) if len(sys.argv) > 3 else 9999

# エージェントインスタンス
agent = GeminiAIAgent(agent_name, agent_role)

# FastAPIアプリケーション
app = FastAPI(title=f"A2A {agent_name}")


def create_agent_card() -> AgentCard:
    """エージェントカードを作成"""
    skill = AgentSkill(
        id="ai_conversation",
        name="AI会話",
        description=f"{agent.role}として会話します",
        tags=["ai", "conversation", "gemini"],
        examples=[
            "技術的な質問をしてください",
            "アイデアを提案してください",
            "問題を分析してください"
        ]
    )
    
    return AgentCard(
        name=agent.name,
        description=f"Gemini AI搭載のA2Aエージェント - {agent.role}",
        url=f"http://localhost:{port}",
        version="2.0.0",
        capabilities=AgentCapabilities(
            streaming=False,
            pushNotifications=False
        ),
        skills=[skill]
    )


@app.on_event("startup")
async def startup_event():
    logger.info("🚀 A0A AIサーバー起動中...")
    logger.info(f"🤖 エージェント名: {agent.name}")
    logger.info(f"📍 エージェントカード: http://localhost:{port}/.well-known/agent.json")


@app.get("/.well-known/agent.json")
async def get_agent_card():
    """エージェントカードを返す (A2A Discovery)"""
    logger.info("🔍 エージェントカードがリクエストされました")
    card = create_agent_card()
    return card


class SendMessageRequest(BaseModel):
    """メッセージ送信リクエスト"""
    id: str
    method: str = "tasks/send"
    params: Dict[str, Any]


@app.post("/tasks/send")
async def send_task(request: SendMessageRequest):
    """タスクを受信して処理 (A2A Task Send)"""
    logger.info("=" * 50)
    logger.info("📨 新しいタスクリクエスト受信")
    logger.info(f"リクエストID: {request.id}")
    
    try:
        # リクエストからメッセージを抽出
        params = request.params
        task_id = params.get("taskId", str(uuid4()))
        message_data = params.get("message", {})
        
        logger.info(f"タスクID: {task_id}")
        
        # メッセージをパース
        if message_data and "parts" in message_data:
            user_text = message_data["parts"][0].get("text", "")
        else:
            user_text = ""
        
        logger.info(f"ユーザーメッセージ: '{user_text}'")
        
        # タスクを作成
        task = Task(
            id=task_id,
            status=TaskStatus.WORKING,
            message=Message(
                role=Role.USER,
                parts=[Part(root=TextPart(text=user_text))]
            )
        )
        agent.tasks[task_id] = task
        logger.info(f"⚙️  タスク処理開始 (ID: {task_id})")
        
        # AIでメッセージを処理
        response_text = await agent.process_message(user_text)
        
        # タスクを完了
        task.status = TaskStatus.COMPLETED
        task.result = Message(
            role=Role.AGENT,
            parts=[Part(root=TextPart(text=response_text))]
        )
        
        logger.info(f"✅ タスク完了 (ID: {task_id})")
        
        # レスポンスを返す
        response = {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": {
                "taskId": task_id,
                "status": task.status.value,
                "message": {
                    "role": task.result.role.value,
                    "parts": [{"text": response_text}]
                }
            }
        }
        
        logger.info("📤 レスポンス送信")
        logger.info("=" * 50)
        
        return response
        
    except Exception as e:
        logger.error(f"❌ エラー発生: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    status = {
        "status": "healthy",
        "agent": agent.name,
        "role": agent.role,
        "ai_model": "gemini-cli",
        "timestamp": datetime.utcnow().isoformat(),
        "tasks_count": len(agent.tasks)
    }
    logger.info(f"💚 ヘルスチェック: {status}")
    return status


if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("🤖 A2A AI Agent Protocol - Gemini搭載")
    print("=" * 60)
    print(f"\n🚀 {agent.name} を起動しています...")
    print(f"📋 役割: {agent.role}")
    print(f"🧠 AIモデル: Gemini CLI")
    print(f"📍 URL: http://localhost:{port}")
    print(f"📋 エージェントカード: http://localhost:{port}/.well-known/agent.json")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")