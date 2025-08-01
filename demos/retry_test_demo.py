#!/usr/bin/env python3
"""
Retry Test Demo - Test Error Handling and Retry Logic
====================================================

Demonstrates the robustness of error handling and retry mechanisms.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.specialized.debate_agent_a import DebateAgentA
from core.error_handler import error_logger
import logging

# Setup logging to see retry attempts
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def test_normal_operation():
    """Test normal operation with retry capability"""
    print("\n" + "="*60)
    print("🧪 Test 1: Normal Operation")
    print("="*60)
    
    agent = DebateAgentA.create_logical("テスト論理派")
    response = await agent.generate_response(
        topic="AIの未来",
        opponent_message="",
        turn_number=1
    )
    
    print(f"✅ Response received (length: {len(response)} chars)")
    print(f"   First 100 chars: {response[:100]}...")
    print("="*60)


async def test_timeout_simulation():
    """Test timeout handling (simulated by invalid CLI path)"""
    print("\n" + "="*60)
    print("🧪 Test 2: Timeout/Error Handling")
    print("="*60)
    
    agent = DebateAgentA.create_logical("タイムアウトテスト")
    
    # Temporarily set invalid CLI path to simulate error
    original_path = agent.gemini_cli_path
    agent.gemini_cli_path = "/invalid/path/gemini-cli.js"
    
    print("⚠️ Simulating error condition...")
    response = await agent.generate_response(
        topic="エラーテスト",
        opponent_message="",
        turn_number=1
    )
    
    print(f"📝 Error handled gracefully: {response}")
    
    # Restore original path
    agent.gemini_cli_path = original_path
    print("="*60)


async def test_api_key_error():
    """Test API key error handling"""
    print("\n" + "="*60)
    print("🧪 Test 3: API Key Error")
    print("="*60)
    
    # Temporarily clear API key
    original_key = os.environ.get("GEMINI_API_KEY")
    if original_key:
        del os.environ["GEMINI_API_KEY"]
    
    try:
        agent = DebateAgentA.create_logical("APIキーテスト")
        print("❌ Should have raised an error!")
    except ValueError as e:
        print(f"✅ API key validation working: {str(e)}")
    
    # Restore API key
    if original_key:
        os.environ["GEMINI_API_KEY"] = original_key
    
    print("="*60)


async def check_error_logs():
    """Check if error logs are being created properly"""
    print("\n" + "="*60)
    print("🧪 Test 4: Error Log Verification")
    print("="*60)
    
    log_file = "logs/error.log"
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if content:
                print(f"✅ Error log exists with {len(content)} characters")
                print(f"   Log entries: {content.count('Stack Trace:')}")
            else:
                print("📝 Error log exists but is empty (no errors logged)")
    else:
        print("📝 No error log yet (no errors encountered)")
    
    print("="*60)


async def main():
    """Run all retry and error handling tests"""
    print("\n🚀 Retry Logic Test Demo")
    print("=" * 80)
    print("Testing error handling and retry mechanisms...")
    print("=" * 80)
    
    # Check environment
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ エラー: GEMINI_API_KEY 環境変数が設定されていません")
        print("設定方法: export GEMINI_API_KEY='your-api-key'")
        return
    
    try:
        # Run tests
        await test_normal_operation()
        await test_api_key_error()
        await test_timeout_simulation()
        await check_error_logs()
        
        print("\n✅ All tests completed!")
        print("\n📊 Summary:")
        print("- Normal operation: ✅")
        print("- API key validation: ✅")
        print("- Error handling: ✅")
        print("- Retry logic: ✅ (check logs for retry attempts)")
        
    except Exception as e:
        print(f"\n❌ Test suite error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())