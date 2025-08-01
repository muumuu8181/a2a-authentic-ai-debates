"""A2A AI同士の会話デモ - 2つのAIエージェントが会話"""
import asyncio
import httpx
import json
from uuid import uuid4
from pprint import pprint
import time


async def send_message_to_agent(agent_url: str, message: str) -> str:
    """エージェントにメッセージを送信して応答を取得"""
    task_id = str(uuid4())
    request_id = str(uuid4())
    
    request_data = {
        "id": request_id,
        "method": "tasks/send",
        "params": {
            "taskId": task_id,
            "message": {
                "role": "user",
                "parts": [{"text": message}]
            }
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{agent_url}/tasks/send",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result and "message" in result["result"]:
                    return result["result"]["message"]["parts"][0]["text"]
            else:
                print(f"Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"通信エラー: {str(e)}")
            return None


async def ai_conversation_demo():
    """2つのAIエージェントによる会話デモ"""
    
    # エージェントのURL
    agent1_url = "http://localhost:9001"  # 研究者エージェント
    agent2_url = "http://localhost:9002"  # 哲学者エージェント
    
    print("\n" + "=" * 70)
    print("🤖 A2A AI Agent 会話デモ - Gemini搭載")
    print("=" * 70)
    print("\n📍 エージェント1（研究者）: http://localhost:9001")
    print("📍 エージェント2（哲学者）: http://localhost:9002")
    print("\n会話を開始します...\n")
    print("=" * 70 + "\n")
    
    # 会話の開始
    conversation_history = []
    current_message = "AIの進化は人類にとってどのような意味を持つと思いますか？"
    
    for turn in range(5):  # 5往復の会話
        print(f"\n--- ターン {turn + 1} ---")
        
        # エージェント1に送信
        print(f"\n👤 → 研究者エージェント: {current_message}")
        response1 = await send_message_to_agent(agent1_url, current_message)
        
        if response1:
            print(f"\n🔬 研究者エージェント: {response1}")
            conversation_history.append(("研究者", response1))
            
            # 少し待機
            await asyncio.sleep(2)
            
            # エージェント2に研究者の応答を送信
            print(f"\n🔬 → 哲学者エージェント: {response1}")
            response2 = await send_message_to_agent(agent2_url, response1)
            
            if response2:
                print(f"\n🤔 哲学者エージェント: {response2}")
                conversation_history.append(("哲学者", response2))
                
                # 次のターンの準備
                current_message = response2
                await asyncio.sleep(2)
            else:
                print("哲学者エージェントからの応答がありません")
                break
        else:
            print("研究者エージェントからの応答がありません")
            break
    
    # 会話のまとめ
    print("\n\n" + "=" * 70)
    print("📝 会話のまとめ")
    print("=" * 70)
    for i, (agent, message) in enumerate(conversation_history):
        print(f"\n{i+1}. {agent}: {message[:100]}...")


async def check_agents_health():
    """エージェントのヘルスチェック"""
    agents = [
        ("研究者エージェント", "http://localhost:9001/health"),
        ("哲学者エージェント", "http://localhost:9002/health")
    ]
    
    print("\n🏥 エージェントのヘルスチェック...")
    all_healthy = True
    
    async with httpx.AsyncClient() as client:
        for name, url in agents:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {name}: {data['status']} (役割: {data['role']})")
                else:
                    print(f"❌ {name}: 応答なし")
                    all_healthy = False
            except Exception as e:
                print(f"❌ {name}: 接続エラー - {str(e)}")
                all_healthy = False
    
    return all_healthy


async def main():
    """メイン関数"""
    print("\n🚀 A2A AI Agent 会話デモを開始します")
    print("\n⚠️  前提条件:")
    print("1. .envファイルにGEMINI_API_KEYが設定されていること")
    print("2. 2つのエージェントが別々のターミナルで起動していること:")
    print("   - ターミナル1: python ai_agent_server.py 研究者エージェント '技術的な観点から分析する研究者' 9001")
    print("   - ターミナル2: python ai_agent_server.py 哲学者エージェント '哲学的な観点から考察する思想家' 9002")
    
    # ヘルスチェック
    if await check_agents_health():
        print("\n✅ すべてのエージェントが正常に動作しています")
        print("\n3秒後に会話を開始します...")
        await asyncio.sleep(3)
        
        # AI同士の会話デモ
        await ai_conversation_demo()
    else:
        print("\n❌ エージェントが起動していません。上記の手順でエージェントを起動してください。")


if __name__ == "__main__":
    asyncio.run(main())