"""
Agent核心模块 - 经典RAG模式（性能优化版）
"""
import os
from typing import List, Dict, Generator

from src.core.llm import get_llm_client
from src.core.knowledge_loader import KnowledgeLoader

# Prompt模板（极简）
SYSTEM_PROMPT = "校园助手，简洁回答。"

USER_PROMPT_TEMPLATE = "资料：{context}\n问：{question}\n答："


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
        """格式化检索结果（精简）"""
        if not search_results:
            return "无"

        # 只取最相关的1条，截断长度
        doc = search_results[0]["document"]
        return doc[:300]  # 限制长度减少token

    def _build_messages(self, question: str, context: str) -> List[Dict]:
        """构建消息"""
        user_message = USER_PROMPT_TEMPLATE.format(context=context, question=question)
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]

    def chat(self, question: str, top_k: int = 2) -> str:
        """同步聊天"""
        search_results = self._get_cached_search(question, top_k)
        context = self._format_context(search_results)
        messages = self._build_messages(question, context)
        return self.llm_client.chat(messages, max_tokens=256)

    def chat_stream(self, question: str, top_k: int = 2) -> Generator[str, None, None]:
        """流式聊天"""
        search_results = self._get_cached_search(question, top_k)
        context = self._format_context(search_results)
        messages = self._build_messages(question, context)
        for chunk in self.llm_client.chat_stream(messages, max_tokens=256):
            yield chunk


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    import time

    agent = CampusAgent()

    questions = ["食堂几点开门？", "选课系统在哪里？", "今天天气怎么样？"]

    for q in questions:
        start = time.time()
        response = agent.chat(q)
        print(f"Q: {q}")
        print(f"时间: {time.time() - start:.2f}秒")
        print(f"A: {response}\n")
