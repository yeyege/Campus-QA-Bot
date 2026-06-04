"""
对话历史管理模块
支持多轮对话、会话持久化
"""
import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict


class ConversationManager:
    """对话历史管理器"""

    def __init__(self, max_history: int = 10, persist_dir: str = "data/conversations"):
        self.max_history = max_history
        self.persist_dir = persist_dir
        self.conversations: Dict[str, List[Dict]] = defaultdict(list)

        # 创建持久化目录
        os.makedirs(persist_dir, exist_ok=True)

    def get_history(self, session_id: str) -> List[Dict]:
        """获取会话历史"""
        if session_id not in self.conversations:
            # 尝试从文件加载
            self._load_from_file(session_id)
        return self.conversations.get(session_id, [])

    def add_message(self, session_id: str, role: str, content: str):
        """添加消息到历史"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.conversations[session_id].append(message)

        # 限制历史长度
        if len(self.conversations[session_id]) > self.max_history * 2:
            self.conversations[session_id] = self.conversations[session_id][-self.max_history * 2:]

        # 持久化
        self._save_to_file(session_id)

    def get_context_messages(self, session_id: str, current_question: str) -> List[Dict]:
        """构建带历史的Prompt消息"""
        history = self.get_history(session_id)

        # 构建历史消息（只取最近N轮）
        messages = []
        recent_history = history[-self.max_history * 2:]

        for msg in recent_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # 添加当前问题
        messages.append({
            "role": "user",
            "content": current_question
        })

        return messages

    def clear_history(self, session_id: str):
        """清除会话历史"""
        if session_id in self.conversations:
            del self.conversations[session_id]
        self._delete_file(session_id)

    def _save_to_file(self, session_id: str):
        """保存到文件"""
        filepath = os.path.join(self.persist_dir, f"{session_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.conversations[session_id], f, ensure_ascii=False, indent=2)

    def _load_from_file(self, session_id: str):
        """从文件加载"""
        filepath = os.path.join(self.persist_dir, f"{session_id}.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                self.conversations[session_id] = json.load(f)

    def list_sessions(self) -> List[str]:
        """列出所有会话"""
        sessions = []
        if os.path.exists(self.persist_dir):
            for file in os.listdir(self.persist_dir):
                if file.endswith(".json"):
                    sessions.append(file.replace(".json", ""))
        return sessions


# 全局实例
conversation_manager = ConversationManager()
