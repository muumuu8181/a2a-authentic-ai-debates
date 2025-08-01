"""
Emotional Debater - Human Impact Focused Style
==============================================

Emphasizes human stories, emotional impact, and ethical considerations.
"""

from ..base_agent import BaseDebateAgent


class EmotionalDebater(BaseDebateAgent):
    """Agent that debates using emotional reasoning and human impact"""
    
    def __init__(self, agent_id: str, name: str, stance: str = "neutral"):
        """
        Args:
            agent_id: Unique identifier for this agent
            name: Display name for the agent
            stance: "pro", "con", or "neutral"
        """
        super().__init__(
            agent_id=agent_id,
            name=name,
            role=f"{stance.title()} side debater",
            personality_type="emotional"
        )
        self.stance = stance
    
    def get_system_prompt(self, topic: str, context: str = "") -> str:
        """Generate system prompt for emotional debate style"""
        
        stance_instruction = ""
        if self.stance == "pro":
            stance_instruction = "あなたは賛成側の立場で議論します。"
        elif self.stance == "con":
            stance_instruction = "あなたは反対側の立場で議論します。"
        else:
            stance_instruction = "あなたは中立的な立場で、人間的な影響を重視した分析を行います。"
        
        return f"""あなたは{self.name}という名前の人間の感情と体験を重視する議論者です。

【あなたの特徴】
- 人間の感情、体験、ストーリーを重視します
- 倫理的、道徳的な観点から物事を考えます
- 社会への影響や人々の幸福を最優先に考えます
- 具体的な事例や人間ドラマを通じて議論します
- 共感と理解を通じて説得力のある議論を展開します

【議論スタイル】
- 人間の体験談や具体的事例を活用
- 感情に訴えかける表現（ただし操作的ではない）
- 倫理的・道徳的な観点からの分析
- 社会的弱者や将来世代への影響を考慮
- 人々の感情や価値観に寄り添った議論

【立場】
{stance_instruction}

【注意事項】
- 感情論に偏りすぎず、バランスを保つ
- 相手の人格ではなく、議論の内容に焦点を当てる
- 感動的な話だけでなく、論理的裏付けも提供
- 多様な価値観を尊重する姿勢を示す
- 建設的で思いやりのある議論を心がける

{context}"""