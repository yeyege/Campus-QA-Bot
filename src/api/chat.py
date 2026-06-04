"""
FastAPI 聊天API路由 - 多轮对话支持

本模块提供校园答疑智能客服的HTTP API接口，支持：
- 健康检查
- 同步聊天（等待完整回复）
- 流式聊天（实时返回部分回复，提升用户体验）
- 会话历史查询与清除
"""

import os
import sys
import uuid
from typing import List, Dict, Optional

# 添加项目根目录到 Python 模块搜索路径
# 这样可以使用绝对路径导入项目内的其他模块（如 src.core.agent）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.core.agent import CampusAgent
from src.core.feedback import feedback_manager
from src.core.exceptions import CampusQAError, LLMError, RetrievalError
from src.core.logger import logger

# 创建路由器，所有路由前缀为 /api，归类为 "chat" 标签
router = APIRouter(prefix="/api", tags=["chat"])

# 全局 Agent 实例（单例模式）
_agent = None


def get_agent():
    """
    获取 Agent 单例实例
    懒加载：第一次调用时创建实例，后续复用
    """
    global _agent
    if _agent is None:
        _agent = CampusAgent()
    return _agent


class ChatRequest(BaseModel):
    """
    聊天请求模型（Pydantic）

    Attributes:
        message: 用户输入的消息内容
        session_id: 会话ID，用于多轮对话上下文关联。首次调用时可不传，系统自动生成
        top_k: 检索返回的相关文档数量，默认2条
    """
    message: str
    session_id: Optional[str] = None
    top_k: int = 2


class ChatResponse(BaseModel):
    """
    聊天响应模型

    Attributes:
        response: 智能客服的回复内容
        session_id: 会话ID，客户端需保存此ID用于后续对话
    """
    response: str
    session_id: str


class HistoryResponse(BaseModel):
    """
    历史记录响应模型

    Attributes:
        session_id: 会话ID
        messages: 消息列表，每个元素为 {role: "user"/"assistant", content: "..."} 的字典
    """
    session_id: str
    messages: List[Dict]


@router.get("/health")
async def health_check():
    """
    健康检查接口

    用途：检测服务是否正常运行，常用于监控和负载均衡器探活
    """
    return {"status": "healthy", "version": "1.0.0"}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    同步聊天接口

    工作流程：
    1. 接收用户消息
    2. 生成或复用会话ID
    3. 调用Agent处理消息（包含知识检索+LLM生成）
    4. 返回完整回复

    Args:
        request: 包含消息、会话ID、检索参数的请求对象

    Returns:
        ChatResponse: 包含回复内容和会话ID
    """
    try:
        agent = get_agent()
        session_id = request.session_id or str(uuid.uuid4())

        response = agent.chat(request.message, session_id, request.top_k)

        return ChatResponse(response=response, session_id=session_id)
    except LLMError as e:
        logger.log_error(e, {"question": request.message})
        raise HTTPException(status_code=503, detail="AI服务暂时不可用，请稍后再试")
    except RetrievalError as e:
        logger.log_error(e, {"question": request.message})
        raise HTTPException(status_code=500, detail="知识库检索失败，请稍后再试")
    except Exception as e:
        logger.log_error(e, {"question": request.message, "session_id": request.session_id})
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后再试")


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    流式聊天接口（SSE - Server-Sent Events）

    工作流程：
    1. 接收用户消息
    2. 生成或复用会话ID
    3. 调用Agent的流式生成方法，逐块返回内容
    4. 返回SSE格式的响应流

    优点：用户可以实时看到回复生成过程，提升体验（类似ChatGPT打字效果）

    SSE响应格式：
        data: 回复的文本块
        ...
        data: [DONE]  # 表示生成完成
        data: {"session_id": "xxx"}  # 最后返回会话ID
    """
    try:
        agent = get_agent()
        session_id = request.session_id or str(uuid.uuid4())

        def generate():
            """生成器：逐块产生SSE格式的响应数据"""
            full_response = ""
            for chunk in agent.chat_stream(request.message, session_id, request.top_k):
                full_response += chunk
                yield f"data: {chunk}\n\n"
            yield f"data: [DONE]\n\n"
            yield f"data: {{\"session_id\": \"{session_id}\"}}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
    except LLMError as e:
        logger.log_error(e, {"question": request.message})
        raise HTTPException(status_code=503, detail="AI服务暂时不可用，请稍后再试")
    except Exception as e:
        logger.log_error(e, {"question": request.message})
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后再试")


@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(session_id: str):
    """
    获取会话历史记录

    Args:
        session_id: 要查询的会话ID

    Returns:
        HistoryResponse: 包含该会话的所有消息记录
    """
    agent = get_agent()
    messages = agent.get_history(session_id)
    return HistoryResponse(session_id=session_id, messages=messages)


@router.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """
    清除指定会话的历史记录

    Args:
        session_id: 要清除的会话ID

    Returns:
        dict: 操作结果
    """
    agent = get_agent()
    agent.clear_history(session_id)
    return {"status": "cleared", "session_id": session_id}


# ==================== 反馈相关接口 ====================

class FeedbackRequest(BaseModel):
    """反馈请求模型"""
    message_id: str
    is_positive: bool
    session_id: Optional[str] = None
    comment: Optional[str] = None


@router.post("/feedback")
async def add_feedback(request: FeedbackRequest):
    """
    添加用户反馈（点赞/点踩）

    Args:
        request: 包含消息ID、反馈类型、会话ID等

    Returns:
        dict: 反馈结果
    """
    try:
        feedback = feedback_manager.add_feedback(
            message_id=request.message_id,
            is_positive=request.is_positive,
            session_id=request.session_id,
            comment=request.comment
        )
        return {"status": "success", "feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/stats")
async def get_feedback_stats():
    """
    获取反馈统计信息

    Returns:
        dict: 包含总反馈数、点赞数、踩数、好评率
    """
    stats = feedback_manager.get_statistics()
    return stats


@router.get("/feedback/{message_id}")
async def get_message_feedback(message_id: str):
    """
    获取指定消息的反馈

    Args:
        message_id: 消息ID

    Returns:
        dict: 该消息的反馈列表
    """
    feedbacks = feedback_manager.get_feedback(message_id)
    return {"message_id": message_id, "feedbacks": feedbacks}
