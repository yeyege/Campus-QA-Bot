# Campus QA Bot - Project Overview

## Project Description
校园答疑智能客服 AI Agent - 一个基于大语言模型的校园答疑系统，采用 RAG（检索增强生成）技术，通过API调用云端大模型实现。

## Tech Stack
- Python 3.10+ / FastAPI / Gradio
- LLM: DeepSeek API (或其他在线API)
- Vector DB: ChromaDB
- Embedding: BGE-large-zh
- Framework: LangChain

## Project Structure
```
campus-qa-bot/
├── config/           # 配置文件
├── knowledge_base/   # 校园FAQ知识库
├── src/
│   ├── api/         # FastAPI 路由
│   ├── core/        # 核心模块(llm, retriever, agent)
│   ├── utils/       # 工具函数
│   └── frontend/    # Gradio 界面
└── docs/            # 开发文档
```

## Documentation
- 开发文档: `docs/开发文档-校园答疑智能客服AI Agent.md`
- 技术路线图: `docs/技术路线图-校园答疑智能客服AI Agent.md`

## Development Mode
User is a beginner (小白), building from scratch. Follow the step-by-step guide in the development docs.
