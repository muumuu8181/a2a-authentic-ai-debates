#!/bin/bash
# A2A AI Agent セットアップと実行スクリプト

echo ""
echo "============================================================"
echo "🤖 A2A AI Agent デモ - Gemini搭載"
echo "============================================================"
echo ""

# .envファイルの確認
if [ ! -f .env ]; then
    echo "❌ .envファイルが見つかりません"
    echo ""
    echo "以下の手順でセットアップしてください:"
    echo "1. cp .env.example .env"
    echo "2. .envファイルを編集してGEMINI_API_KEYを設定"
    echo "   (APIキーは https://makersuite.google.com/app/apikey から取得)"
    echo ""
    exit 1
fi

# APIキーの確認
if ! grep -q "GEMINI_API_KEY=.*[^=]" .env; then
    echo "❌ GEMINI_API_KEYが設定されていません"
    echo ".envファイルを編集してAPIキーを設定してください"
    exit 1
fi

echo "✅ 環境設定OK"
echo ""

# Pythonパッケージのインストール
echo "📦 必要なパッケージをインストール中..."
source .venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

echo ""
echo "🚀 AIエージェントを起動するには、以下のコマンドを別々のターミナルで実行してください:"
echo ""
echo "# ターミナル1 (研究者エージェント)"
echo "cd ~/a2a-demo && source .venv/bin/activate"
echo "python ai_agent_server.py '研究者エージェント' '技術的な観点から分析する研究者' 9001"
echo ""
echo "# ターミナル2 (哲学者エージェント)"
echo "cd ~/a2a-demo && source .venv/bin/activate"
echo "python ai_agent_server.py '哲学者エージェント' '哲学的な観点から考察する思想家' 9002"
echo ""
echo "# ターミナル3 (会話デモ)"
echo "cd ~/a2a-demo && source .venv/bin/activate"
echo "python ai_conversation_demo.py"
echo ""
echo "============================================================"