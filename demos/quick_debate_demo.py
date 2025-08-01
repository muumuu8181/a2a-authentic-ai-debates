#!/usr/bin/env python3
"""
Quick Debate Demo - AI vs AI Discussion Test
============================================

Demonstrates the AI debate system with a simple 2-agent discussion.
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.session_manager import SessionManager
from agents.specialized.debate_agent_a import DebateAgentA  
from agents.specialized.debate_agent_b import DebateAgentB


async def run_debate_demo():
    """Run a quick AI vs AI debate demonstration"""
    
    print("\n" + "=" * 80)
    print("🤖 AI vs AI Debate Demo - Gemini CLI Powered")
    print("=" * 80)
    print("Topic: AIは人類の味方か？")
    print("Participants: 論理派(賛成) vs 感情派(反対)")
    print("=" * 80 + "\n")
    
    # Initialize session manager
    session_manager = SessionManager()
    
    # Create debate agents
    pro_agent = DebateAgentA.create_logical("テクノ楽観主義者")
    con_agent = DebateAgentB.create_emotional("ヒューマン擁護者")
    
    print(f"✅ {pro_agent.name} (論理派・賛成側) 準備完了")
    print(f"✅ {con_agent.name} (感情派・反対側) 準備完了\n")
    
    # Load scenario
    scenario_path = "discussions/scenarios/ai_humanity_ally.json"
    with open(scenario_path, 'r', encoding='utf-8') as f:
        scenario = json.load(f)
    
    # Create session
    participants = [
        {"id": pro_agent.agent_id, "name": pro_agent.name, "role": "pro"},
        {"id": con_agent.agent_id, "name": con_agent.name, "role": "con"}
    ]
    
    session = session_manager.create_session(
        topic=scenario["title"],
        participants=participants,
        max_turns=4  # 2 turns each for demo
    )
    
    print(f"🎯 議論セッション開始: {session.session_id}")
    print(f"📝 トピック: {scenario['title']}\n")
    
    # Start the debate
    topic = scenario["title"]
    current_message = ""
    
    for turn in range(4):  # 4 turns total (2 each)
        turn_number = turn + 1
        
        if turn % 2 == 0:  # Pro agent's turn
            agent = pro_agent
            print(f"--- ターン {turn_number}: {agent.name} の主張 ---")
        else:  # Con agent's turn  
            agent = con_agent
            print(f"--- ターン {turn_number}: {agent.name} の反論 ---")
        
        print(f"🤔 {agent.name} が考え中...")
        
        # Generate response
        response = await agent.generate_response(
            topic=topic,
            opponent_message=current_message,
            context=scenario.get("context", ""),
            turn_number=turn_number
        )
        
        print(f"\n💬 {agent.name}:")
        print("-" * 60)
        print(response)
        print("-" * 60 + "\n")
        
        # Add turn to session
        session_manager.add_turn(
            session_id=session.session_id,
            agent_id=agent.agent_id,
            agent_name=agent.name,
            message=response,
            response_time=2.0  # Approximate response time
        )
        
        # Update current message for next agent
        current_message = response
        
        # Brief pause between turns
        if turn < 3:
            print("⏳ 次のターンまで3秒待機...\n")
            await asyncio.sleep(3)
    
    # Get final session summary
    summary = session_manager.get_session_summary(session.session_id)
    
    print("=" * 80)
    print("🎉 議論完了！")
    print("=" * 80)
    print(f"📊 総ターン数: {summary['turn_count']}")
    print(f"💾 セッションID: {summary['session_id']}")
    print(f"📁 保存場所: discussions/completed/{summary['session_id']}.json")
    print("=" * 80 + "\n")
    
    print("🏆 議論の振り返り:")
    print("- 論理派は事実とデータで攻める")
    print("- 感情派は人間への影響で反論")
    print("- 異なるアプローチが見事に対比")
    print("- 完全な議論ログが保存済み")
    
    return session.session_id


async def main():
    """Main function"""
    print("🚀 Quick Debate Demo 開始")
    
    # Check environment
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ エラー: GEMINI_API_KEY 環境変数が設定されていません")
        print("設定方法: export GEMINI_API_KEY='your-api-key'")
        return
    
    try:
        session_id = await run_debate_demo()
        print(f"\n✅ デモ完了！セッションID: {session_id}")
        
    except Exception as e:
        print(f"\n❌ デモ実行エラー: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())