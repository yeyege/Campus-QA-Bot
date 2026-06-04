"""
Agent核心模块 - 多轮对话支持
"""
import os
import hashlib
import time
from typing import List, Dict, Generator, Optional

from src.core.llm import get_llm_client
from src.core.knowledge_loader import KnowledgeLoader
from src.core.conversation import conversation_manager
from src.core.feedback import feedback_manager
from src.core.logger import logger
from src.core.exceptions import LLMError, RetrievalError

# Prompt模板
SYSTEM_PROMPT = """你是校园智能助手"小智"，专注于校园知识问答。

回答规则：
1. 如果有参考资料，基于资料简洁回答
2. 如果没有资料，用你的知识回答基础常识问题（如1+1=2、北京是首都）
3. 实时信息问题（如今天日期、天气）：说明无法获取，建议查看手机
4. 超出范围问题：礼貌引导回校园话题

语气：友好亲切，像学长学姐"""


class CampusAgent:
    def __init__(self, llm_provider: str = None):
        self.llm_client = get_llm_client(llm_provider)
        self.knowledge_loader = KnowledgeLoader()
        self.knowledge_loader.init_chromadb()
        self.knowledge_loader.load_embedding_model()

        # 检索缓存
        self._search_cache = {}

    def _get_cached_search(self, question: str, top_k: int = 2) -> List[dict]:
        """获取缓存的检索结果"""
        cache_key = f"{question}_{top_k}"
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]

        results = self.knowledge_loader.search(question, top_k)
        self._search_cache[cache_key] = results
        return results

    def _format_context(self, search_results: List[dict]) -> str:
        """格式化检索结果"""
        if not search_results:
            return "无相关资料"

        # 检查检索结果是否相关（距离越小越相关）
        best_distance = search_results[0]["distance"]
        if best_distance > 1.0:  # 阈值，超过表示不相关
            return "无相关资料"

        doc = search_results[0]["document"]
        return doc[:300]

    def _build_messages_with_history(self, session_id: str, question: str, context: str) -> List[Dict]:
        """构建带历史的消息"""
        # 获取历史对话
        history = conversation_manager.get_history(session_id)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # 添加历史对话（最近4轮）
        recent = history[-8:] if len(history) > 8 else history
        for msg in recent:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # 添加当前带上下文的问题
        user_message = f"资料：{context}\n问：{question}\n答："
        messages.append({"role": "user", "content": user_message})

        return messages

    def chat(self, question: str, session_id: str = "default", top_k: int = 2) -> str:
        """多轮对话聊天"""
        start_time = time.time()

        try:
            # 检索知识库
            search_results = self._get_cached_search(question, top_k)
            context = self._format_context(search_results)

            logger.log_retrieval(question, len(search_results), search_results[0]["distance"] if search_results else 0)

            # 构建带历史的消息
            messages = self._build_messages_with_history(session_id, question, context)

            # 调用LLM
            response = self.llm_client.chat(messages, max_tokens=256)

            # 保存对话历史
            conversation_manager.add_message(session_id, "user", question)
            conversation_manager.add_message(session_id, "assistant", response)

            latency = time.time() - start_time
            logger.log_request(question, response, latency, session_id)

            return response
        except Exception as e:
            if "LLM" in str(type(e).__name__) or "API" in str(type(e).__name__):
                raise LLMError(str(e))
            raise

    def chat_stream(self, question: str, session_id: str = "default", top_k: int = 2) -> Generator[str, None, None]:
        """多轮对话流式聊天"""
        start_time = time.time()

        try:
            # 检索知识库
            search_results = self._get_cached_search(question, top_k)
            context = self._format_context(search_results)

            logger.log_retrieval(question, len(search_results), search_results[0]["distance"] if search_results else 0)

            # 构建带历史的消息
            messages = self._build_messages_with_history(session_id, question, context)

            # 流式调用LLM
            full_response = ""
            for chunk in self.llm_client.chat_stream(messages, max_tokens=256):
                full_response += chunk
                yield chunk

            # 保存对话历史
            conversation_manager.add_message(session_id, "user", question)
            conversation_manager.add_message(session_id, "assistant", full_response)

            latency = time.time() - start_time
            logger.log_request(question, full_response, latency, session_id)
        except Exception as e:
            if "LLM" in str(type(e).__name__) or "API" in str(type(e).__name__):
                raise LLMError(str(e))
            raise

    def get_history(self, session_id: str) -> List[Dict]:
        """获取对话历史"""
        return conversation_manager.get_history(session_id)

    def clear_history(self, session_id: str):
        """清除对话历史"""
        conversation_manager.clear_history(session_id)
        # 同时清除该session的检索缓存
        keys_to_delete = [k for k in self._search_cache.keys()]
        for key in keys_to_delete:
            del self._search_cache[key]


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    import time

    agent = CampusAgent()
    session_id = "test_session"

    # 模拟多轮对话
    conversations = [
        "食堂几点开门？",
        "那图书馆呢？",
        "它可以借多少本书？",
    ]

    for q in conversations:
        start = time.time()
        response = agent.chat(q, session_id)
        print(f"Q: {q}")
        print(f"A: {response}")
        print(f"时间: {time.time() - start:.2f}秒\n")

    # 显示完整历史
    print("=== 对话历史 ===")
    history = agent.get_history(session_id)
    for msg in history:
        print(f"[{msg['role']}] {msg['content'][:50]}...")
