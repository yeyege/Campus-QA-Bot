"""
FastAPI 聊天API路由
"""
import os
import sys
import uuid
from datetime import datetime
from typing import List, Dict, Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.core.agent import CampusAgent

router = APIRouter(prefix="/api", tags=["chat"])

# 全局Agent实例（延迟加载）
_agent = None


def get_agent():
    """获取Agent实例"""
    global _agent
    if _agent is None:
        _agent = CampusAgent()
    return _agent


# 会话存储
conversations: Dict[str, List[Dict]] = {}


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str
    session_id: Optional[str] = None
    top_k: int = 3


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str
    session_id: str
    sources: List[dict] = []


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """同步聊天接口"""
    try:
        agent = get_agent()

        # 生成或使用session_id
        session_id = request.session_id or str(uuid.uuid4())

        # 获取检索结果
        search_results = agent._get_cached_search(request.message, request.top_k)

        # 调用LLM生成回答
        response = agent.chat(request.message, request.top_k)

        # 保存会话历史
        if session_id not in conversations:
            conversations[session_id] = []

        conversations[session_id].append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now().isoformat()
        })
        conversations[session_id].append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })

        return ChatResponse(
            response=response,
            session_id=session_id,
            sources=[
                {
                    "category": r["metadata"]["category"],
                    "question": r["metadata"]["question"],
                    "score": 1 - r["distance"]
                }
                for r in search_results
            ]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """流式聊天接口"""
    try:
        agent = get_agent()

        # 生成或使用session_id
        session_id = request.session_id or str(uuid.uuid4())

        def generate():
            response = ""
            for chunk in agent.chat_stream(request.message, request.top_k):
                response += chunk
                yield f"data: {chunk}\n\n"

            # 保存会话历史
            if session_id not in conversations:
                conversations[session_id] = []

            conversations[session_id].append({
                "role": "user",
                "content": request.message,
                "timestamp": datetime.now().isoformat()
            })
            conversations[session_id].append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })

            yield f"data: [DONE]\n\n"
            yield f"data: {{\"session_id\": \"{session_id}\"}}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """获取会话历史"""
    if session_id not in conversations:
        return {"session_id": session_id, "messages": []}

    return {
        "session_id": session_id,
        "messages": conversations[session_id]
    }


@router.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """清除会话历史"""
    if session_id in conversations:
        del conversations[session_id]
    return {"status": "cleared"}
