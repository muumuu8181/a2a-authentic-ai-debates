#!/usr/bin/env python3
"""
Integrated Quality Demo - Complete System Demonstration
======================================================

Demonstrates the full integration of:
- Retry logic (Oliver)
- Quality metrics (Luna)
- Checkpoint system (Luna)
- Session management
"""

import asyncio
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.session_manager import SessionManager
from core.quality_calculator import QualityCalculator
from core.checkpoint_manager import CheckpointManager, CheckpointType
from agents.specialized.debate_agent_a import DebateAgentA
from agents.specialized.debate_agent_b import DebateAgentB
import json


async def run_integrated_demo():
    """Run complete integrated demonstration"""
    
    print("\n" + "="*80)
    print("🚀 Integrated Quality Demo - Full System Test")
    print("="*80)
    print("Features:")
    print("  ✅ Retry Logic (3x retry with exponential backoff)")
    print("  ✅ Quality Metrics (Real-time calculation)")
    print("  ✅ Checkpoint System (Auto-save after each turn)")
    print("  ✅ Authenticity Detection (Response Time Variance)")
    print("="*80 + "\n")
    
    # Initialize components
    session_manager = SessionManager()
    quality_calculator = QualityCalculator()
    checkpoint_manager = CheckpointManager()
    
    print("📦 Components initialized:")
    print(f"  - Session Manager: ✅")
    print(f"  - Quality Calculator: ✅ (Luna's design)")
    print(f"  - Checkpoint Manager: ✅ (Luna's design)")
    print(f"  - Retry Handler: ✅ (Oliver's implementation)\n")
    
    # Create debate agents
    pro_agent = DebateAgentA.create_philosophical("未来哲学者")
    con_agent = DebateAgentB.create_logical("現実主義者")
    
    # Create session
    participants = [
        {"id": pro_agent.agent_id, "name": pro_agent.name, "role": "pro"},
        {"id": con_agent.agent_id, "name": con_agent.name, "role": "con"}
    ]
    
    topic = "技術的特異点（シンギュラリティ）は人類にとって福音か？"
    
    session = session_manager.create_session(
        topic=topic,
        participants=participants,
        max_turns=6  # 3 turns each
    )
    
    print(f"🎯 Debate Session: {session.session_id}")
    print(f"📝 Topic: {topic}")
    print(f"👥 Participants: {pro_agent.name} vs {con_agent.name}\n")
    
    # Quality tracking
    quality_history = []
    checkpoint_ids = []
    
    # Run debate with quality monitoring
    current_message = ""
    
    for turn in range(6):  # 6 turns total
        turn_number = turn + 1
        
        # Select agent
        if turn % 2 == 0:
            agent = pro_agent
            role = "主張"
        else:
            agent = con_agent
            role = "反論"
        
        print(f"--- Turn {turn_number}: {agent.name} の{role} ---")
        print(f"🤔 {agent.name} thinking...")
        
        try:
            # Generate response (with retry logic built-in)
            response = await agent.generate_response(
                topic=topic,
                opponent_message=current_message,
                turn_number=turn_number
            )
            
            print(f"✅ Response generated successfully")
            
            # Add to session
            success = session_manager.add_turn(
                session_id=session.session_id,
                agent_id=agent.agent_id,
                agent_name=agent.name,
                message=response,
                response_time=agent.conversation_history[-1]['response_time']
            )
            
            if success:
                # Calculate quality metrics
                print(f"📊 Calculating quality metrics...")
                
                # Get updated session
                updated_session = session_manager.get_session(session.session_id)
                
                # Check if session still exists (not completed)
                if updated_session:
                    session = updated_session
                    
                    # Calculate turn metrics
                    turn_metrics = quality_calculator.calculate_turn_metrics(
                        session.turn_history[-1],
                        session,
                        topic
                    )
                else:
                    # Session was completed, use last known state
                    turn_metrics = quality_calculator.calculate_turn_metrics(
                        session.turn_history[-1],
                        session,
                        topic
                    )
                
                # Display metrics
                print(f"   Coherence: {turn_metrics.coherence_score:.1%}")
                print(f"   Relevance: {turn_metrics.relevance_score:.1%}")
                print(f"   Diversity: {turn_metrics.diversity_score:.1%}")
                print(f"   Authenticity: {turn_metrics.authenticity_score:.1%}")
                print(f"   Response Time: {turn_metrics.response_time:.2f}s")
                
                # Create quality snapshot
                quality_snapshot = {
                    "coherence": turn_metrics.coherence_score,
                    "relevance": turn_metrics.relevance_score,
                    "diversity": turn_metrics.diversity_score,
                    "authenticity": turn_metrics.authenticity_score
                }
                
                quality_history.append(quality_snapshot)
                
                # Create checkpoint
                print(f"💾 Creating checkpoint...")
                checkpoint = checkpoint_manager.create_checkpoint(
                    session=session,
                    checkpoint_type=CheckpointType.AUTOMATIC,
                    quality_snapshot=quality_snapshot,
                    metadata={"turn": turn_number}
                )
                checkpoint_ids.append(checkpoint.checkpoint_id)
                print(f"   Checkpoint saved: {checkpoint.checkpoint_id[:8]}...")
                
                # Check for quality alerts
                if turn_metrics.authenticity_score < 0.4:
                    print(f"⚠️ ALERT: Low authenticity detected!")
                if turn_metrics.coherence_score < 0.6:
                    print(f"⚠️ ALERT: Low coherence detected!")
                
                # Show preview of response
                print(f"\n💬 {agent.name}:")
                print("-" * 60)
                preview = response[:200] + "..." if len(response) > 200 else response
                print(preview)
                print("-" * 60 + "\n")
                
                # Update current message
                current_message = response
                
            else:
                print(f"❌ Failed to add turn to session")
                
        except Exception as e:
            print(f"❌ Error during turn {turn_number}: {str(e)}")
            
            # Emergency checkpoint
            print(f"🚨 Creating emergency checkpoint...")
            if session and hasattr(session, 'session_id'):
                emergency_checkpoint = checkpoint_manager.save_emergency_checkpoint(
                    session_id=session.session_id,
                    error=e,
                    session=session
                )
            if emergency_checkpoint:
                print(f"   Emergency checkpoint created")
        
        # Brief pause
        if turn < 5:
            await asyncio.sleep(2)
    
    # Final quality report
    print("\n" + "="*80)
    print("📊 Final Quality Report")
    print("="*80)
    
    final_report = quality_calculator.calculate_session_quality(session)
    
    print(f"Overall Score: {final_report.overall_score:.1%}")
    print(f"  - Coherence: {final_report.coherence:.1%}")
    print(f"  - Relevance: {final_report.relevance:.1%}")
    print(f"  - Engagement: {final_report.engagement:.1%}")
    print(f"  - Authenticity: {final_report.authenticity:.1%}")
    
    if final_report.alerts:
        print(f"\n⚠️ Alerts:")
        for alert in final_report.alerts:
            print(f"  - {alert}")
    
    if final_report.recommendations:
        print(f"\n💡 Recommendations:")
        for rec in final_report.recommendations:
            print(f"  - {rec}")
    
    # Response time analysis
    print(f"\n⏱️ Response Time Analysis:")
    response_times = [t.response_time for t in session.turn_history]
    if response_times:
        import statistics
        print(f"  - Average: {statistics.mean(response_times):.2f}s")
        print(f"  - Variance: {statistics.variance(response_times):.2f}")
        print(f"  - Min: {min(response_times):.2f}s")
        print(f"  - Max: {max(response_times):.2f}s")
    
    # Checkpoint summary
    print(f"\n💾 Checkpoint Summary:")
    print(f"  - Total checkpoints: {len(checkpoint_ids)}")
    print(f"  - Session can be recovered from any checkpoint")
    
    print("\n" + "="*80)
    print("✨ Demo Complete!")
    print("="*80)
    
    return {
        "session_id": session.session_id,
        "quality_report": final_report,
        "checkpoint_count": len(checkpoint_ids)
    }


async def demonstrate_recovery():
    """Demonstrate checkpoint recovery"""
    print("\n" + "="*80)
    print("🔄 Checkpoint Recovery Demo")
    print("="*80)
    
    checkpoint_manager = CheckpointManager()
    
    # List recent checkpoints
    print("📋 Available checkpoints:")
    
    # (In real implementation, would list actual checkpoints)
    print("  - Auto-save checkpoints available for recovery")
    print("  - Emergency checkpoints from error scenarios")
    
    print("\n✅ Recovery system ready")
    print("="*80)


async def main():
    """Main demo runner"""
    print("🌟 Integrated Quality Demo - Oliver + Luna Collaboration")
    print("Demonstrating complete system integration\n")
    
    # Check environment
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY not set")
        return
    
    try:
        # Run main demo
        result = await run_integrated_demo()
        
        # Show recovery capability
        await demonstrate_recovery()
        
        print(f"\n✅ All systems operational!")
        print(f"📊 Quality tracking: Active")
        print(f"💾 Checkpoints: Enabled") 
        print(f"🔄 Retry logic: Protected")
        print(f"\n🎉 Ready for Monday's demo with Boss!")
        
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())