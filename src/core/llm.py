"""
大模型封装模块 - 支持小米Mimo API（极速版）
"""
import os
import time
import requests
from dotenv import load_dotenv
from typing import List, Dict, Generator
from concurrent.futures import ThreadPoolExecutor

# 加载环境变量
load_dotenv("config/.env")

# 全局连接池
_executor = ThreadPoolExecutor(max_workers=2)


class LLMClient:
    """大模型客户端基类"""

    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.last_request_time = 0
        self.min_interval = 0.3

    def _wait_if_needed(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()

    def chat(self, messages: List[Dict], temperature: float = 0.5, max_tokens: int = 256) -> str:
        raise NotImplementedError

    def chat_stream(self, messages: List[Dict], temperature: float = 0.5, max_tokens: int = 256) -> Generator[str, None, None]:
        raise NotImplementedError


class XiaomiMimoClient(LLMClient):
    """小米Mimo API客户端 - 极速优化"""

    def __init__(self):
        api_key = os.getenv("XIAOMI_API_KEY")
        base_url = os.getenv("XIAOMI_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1")
        self.model = os.getenv("XIAOMI_MODEL", "mimo-v2.5")
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "256"))
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.5"))
        super().__init__(api_key, base_url)
        self.session = requests.Session()

    def _make_request(self, data: dict, stream: bool = False):
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self._wait_if_needed()
        response = self.session.post(url, headers=headers, json=data, stream=stream, timeout=20)
        response.raise_for_status()
        return response

    def chat(self, messages: List[Dict], temperature: float = None, max_tokens: int = None) -> str:
        """同步聊天"""
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens
        }
        response = self._make_request(data, stream=False)
        result = response.json()
        message = result["choices"][0]["message"]
        return message.get("content", "") or ""

    def chat_stream(self, messages: List[Dict], temperature: float = None, max_tokens: int = None) -> Generator[str, None, None]:
        """流式聊天"""
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            "stream": True
        }
        response = self._make_request(data, stream=True)

        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    line = line[6:]
                if line == "[DONE]":
                    break
                try:
                    import json
                    chunk = json.loads(line)
                    if "choices" in chunk and chunk["choices"]:
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                except:
                    continue


def get_llm_client(provider: str = None) -> LLMClient:
    if provider is None:
        provider = os.getenv("LLM_PROVIDER", "xiaomi")
    if provider == "xiaomi":
        return XiaomiMimoClient()
    else:
        raise ValueError(f"不支持的LLM提供商: {provider}")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    client = get_llm_client()
    print(f"模型: {client.model}, max_tokens: {client.max_tokens}")

    messages = [{"role": "user", "content": "你好"}]
    start = time.time()
    response = client.chat(messages)
    print(f"响应时间: {time.time() - start:.2f}秒")
    print(f"回复: {response}")
