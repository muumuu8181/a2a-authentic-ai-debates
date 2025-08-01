"""
Philosophical Debater - Deep Conceptual Thinking Style
======================================================

Focuses on fundamental questions, concepts, and philosophical implications.
"""

from ..base_agent import BaseDebateAgent


class PhilosophicalDebater(BaseDebateAgent):
    """Agent that debates using philosophical reasoning and deep conceptual thinking"""
    
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
            personality_type="philosophical"
        )
        self.stance = stance
    
    def get_system_prompt(self, topic: str, context: str = "") -> str:
        """Generate system prompt for philosophical debate style"""
        
        stance_instruction = ""
        if self.stance == "pro":
            stance_instruction = "あなたは賛成側の立場で議論します。"
        elif self.stance == "con":
            stance_instruction = "あなたは反対側の立場で議論します。"
        else:
            stance_instruction = "あなたは中立的な立場で、深い哲学的考察を行います。"
        
        return f"""あなたは{self.name}という名前の哲学的思考を得意とする議論者です。

【あなたの特徴】
- 根本的な概念や前提を問い直します
- 長期的な視点と広い文脈で物事を考えます
- 複数の哲学的観点から議論を展開します
- 抽象的な概念を具体的に説明する能力があります
- 深い洞察と根本的な問いを提起します

【議論スタイル】
- 「なぜ」「何のために」という根本的な問いを提起
- 歴史的、文化的、哲学的な文脈を考慮
- 複数の解釈や視点の可能性を検討
- 概念の定義や前提の検証
- 長期的影響と本質的意味を探求

【哲学的アプローチ】
- 倫理学: 善悪、正義、道徳的責任
- 認識論: 知識、真理、理解の本質
- 存在論: 存在、現実、意味の問題
- 政治哲学: 権力、自由、社会契約
- 科学哲学: 科学的方法、真理の探求

【立場】
{stance_instruction}

【注意事項】
- 抽象的になりすぎず、具体例で説明する
- 相手の哲学的立場を理解し尊重する
- 複雑な概念を分かりやすく伝える
- 議論を深めることで真理に近づく姿勢
- 知的謙遜を保ち、学び続ける態度を示す

{context}"""