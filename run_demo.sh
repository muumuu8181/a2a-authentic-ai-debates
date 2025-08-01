#!/bin/bash
# A2Aデモ実行スクリプト

echo "=== A2A Agent-to-Agent プロトコル デモ ==="
echo ""
echo "1. A2Aエージェントサーバーを起動します..."
echo ""

cd ~/a2a-demo
source .venv/bin/activate

# サーバーを起動（ログを表示）
python agent_server.py