"""
用户反馈模块 - 支持点赞/点踩反馈收集
"""
import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict


class FeedbackManager:
    """反馈管理器"""

    def __init__(self, persist_dir: str = "data/feedback"):
        self.persist_dir = persist_dir
        self.feedback_store: Dict[str, List[Dict]] = defaultdict(list)

        os.makedirs(persist_dir, exist_ok=True)
        self._load_all_feedback()

    def add_feedback(self, message_id: str, is_positive: bool, session_id: str = None, comment: str = None) -> Dict:
        """添加反馈"""
        feedback = {
            "message_id": message_id,
            "is_positive": is_positive,
            "session_id": session_id,
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }

        self.feedback_store[message_id].append(feedback)
        self._save_to_file(message_id)

        return feedback

    def get_feedback(self, message_id: str) -> List[Dict]:
        """获取消息的反馈"""
        return self.feedback_store.get(message_id, [])

    def get_statistics(self) -> Dict:
        """获取反馈统计"""
        total = 0
        positive = 0
        negative = 0

        for feedbacks in self.feedback_store.values():
            for fb in feedbacks:
                total += 1
                if fb["is_positive"]:
                    positive += 1
                else:
                    negative += 1

        return {
            "total": total,
            "positive": positive,
            "negative": negative,
            "positive_rate": f"{(positive/total*100):.1f}%" if total > 0 else "0%"
        }

    def _save_to_file(self, message_id: str):
        """保存到文件"""
        filepath = os.path.join(self.persist_dir, f"{message_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.feedback_store[message_id], f, ensure_ascii=False, indent=2)

    def _load_all_feedback(self):
        """加载所有反馈"""
        if os.path.exists(self.persist_dir):
            for file in os.listdir(self.persist_dir):
                if file.endswith(".json"):
                    message_id = file.replace(".json", "")
                    filepath = os.path.join(self.persist_dir, file)
                    with open(filepath, "r", encoding="utf-8") as f:
                        self.feedback_store[message_id] = json.load(f)


# 全局实例
feedback_manager = FeedbackManager()
