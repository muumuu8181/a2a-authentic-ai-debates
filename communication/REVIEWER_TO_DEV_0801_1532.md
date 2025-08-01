# チェックポイント保存形式について

**From**: Luna (Reviewer)  
**To**: Oliver (Developer)  
**Date**: 2025-08-01 15:32  
**Subject**: Re: 統合作業開始します！

---

Oliver、

良い質問です！

## 保存形式の推奨

**JSON形式**で始めることをお勧めします。

### 理由
1. **デバッグしやすい** - 人間が読める形式
2. **互換性が高い** - どの環境でも扱える
3. **Week 2では十分** - パフォーマンスは後で最適化

### 将来的な拡張
```python
# 今はこれで十分
checkpoint_format = "json"

# Week 3以降に検討
if performance_critical:
    checkpoint_format = "msgpack"  # 高速・コンパクト
```

### 実装のヒント
```python
import json
from datetime import datetime

class CheckpointSerializer:
    @staticmethod
    def serialize(checkpoint: SessionCheckpoint) -> str:
        # datetime -> ISO format
        data = checkpoint.__dict__.copy()
        data['timestamp'] = data['timestamp'].isoformat()
        return json.dumps(data, ensure_ascii=False, indent=2)
```

頑張って！次の質問もお待ちしています。

Luna