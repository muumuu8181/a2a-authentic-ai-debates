#!/usr/bin/env python3
"""
Personality Test Demo - Different Agent Personality Combinations
=============================================================

Tests various personality combinations in AI debates.
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


async def test_personality_combination(pro_personality, con_personality, topic="技術進歩は人類の幸福に必要か？"):
    """Test a specific personality combination"""
    
    print(f"\n{'='*80}")
    print(f"🧪 性格テスト: {pro_personality.upper()} vs {con_personality.upper()}")
    print(f"{'='*80}")
    print(f"トピック: {topic}")
    print(f"{'='*80}\n")
    
    # Initialize session manager
    session_manager = SessionManager()
    
    # Create agents with different personalities
    pro_agent = DebateAgentA.create_default(pro_personality, f"{pro_personality.title()}賛成派")
    con_agent = DebateAgentB.create_default(con_personality, f"{con_personality.title()}反対派")
    
    print(f"✅ {pro_agent.name} (賛成側) 準備完了")
    print(f"✅ {con_agent.name} (反対側) 準備完了\n")
    
    # Create session
    participants = [
        {"id": pro_agent.agent_id, "name": pro_agent.name, "role": "pro"},
        {"id": con_agent.agent_id, "name": con_agent.name, "role": "con"}
    ]
    
    session = session_manager.create_session(
        topic=topic,
        participants=participants,
        max_turns=4  # 2 turns each for quick test
    )
    
    print(f"🎯 セッション開始: {session.session_id}")
    print(f"📝 トピック: {topic}\n")
    
    # Start the debate
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
            context="",
            turn_number=turn_number
        )
        
        print(f"\n💬 {agent.name}:")
        print("-" * 60)
        # Show first 200 characters only for demo 
        response_preview = response[:200] + "..." if len(response) > 200 else response
        print(response_preview)
        print("-" * 60 + "\n")
        
        # Add turn to session
        session_manager.add_turn(
            session_id=session.session_id,
            agent_id=agent.agent_id,
            agent_name=agent.name,
            message=response,
            response_time=1.5
        )
        
        # Update current message for next agent
        current_message = response
        
        # Brief pause between turns
        if turn < 3:
            await asyncio.sleep(2)
    
    # Get final session summary
    summary = session_manager.get_session_summary(session.session_id)
    
    print("=" * 80)
    print(f"🎉 {pro_personality.upper()} vs {con_personality.upper()} 議論完了！")
    print("=" * 80)
    print(f"📊 総ターン数: {summary['turn_count']}")
    print(f"💾 セッションID: {summary['session_id']}")
    print("=" * 80 + "\n")
    
    return session.session_id


async def main():
    """Main function to test different personality combinations"""
    print("🚀 Personality Test Demo 開始")
    
    # Check environment
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ エラー: GEMINI_API_KEY 環境変数が設定されていません")
        print("設定方法: export GEMINI_API_KEY='your-api-key'")
        return
    
    try:
        # Test different personality combinations
        combinations = [
            ("logical", "emotional"),      # 論理 vs 感情
            ("philosophical", "logical"),  # 哲学 vs 論理
            ("emotional", "philosophical") # 感情 vs 哲学
        ]
        
        topics = [
            "技術進歩は人類の幸福に必要か？",
            "個人の自由と社会の安全のバランス",
            "伝統的価値観の現代社会での意義"
        ]
        
        session_ids = []
        
        for i, (pro_personality, con_personality) in enumerate(combinations):
            topic = topics[i % len(topics)]
            
            session_id = await test_personality_combination(
                pro_personality, 
                con_personality, 
                topic
            )
            session_ids.append(session_id)
            
            # Pause between tests
            if i < len(combinations) - 1:
                print("⏳ 次のテストまで5秒待機...\n")
                await asyncio.sleep(5)
        
        # Final summary
        print("🎯 全テスト完了！")
        print("📋 セッションID一覧:")
        for session_id in session_ids:
            print(f"  - {session_id}")
        print("\n✨ 各性格の特徴がよく表れた議論ができました！")
        
    except Exception as e:
        print(f"\n❌ デモ実行エラー: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())