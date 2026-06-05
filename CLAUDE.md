# Campus QA Bot - Project Overview

## Project Description
校园答疑智能客服 AI Agent - 一个基于大语言模型的校园答疑系统，采用 RAG（检索增强生成）技术，通过API调用小米Mimo云端大模型实现。支持多轮对话、流式输出、会话持久化。

## Tech Stack
- Python 3.10+ / FastAPI / Gradio (备用)
- LLM: 小米 Mimo API (mimo-v2.5)
- Vector DB: ChromaDB (嵌入式)
- Embedding: BGE-small-zh-v1.5
- 前端: 自定义 HTML/CSS/JS (类ChatGPT风格)

## Project Structure
```
campus-qa-bot/
├── config/                # 配置文件 (.env, config.yaml)
├── knowledge_base/        # 校园FAQ知识库 (7个分类, 100+问答)
│   ├── faq/              # Markdown FAQ文档
│   └── processed/        # ChromaDB向量化数据
├── src/
│   ├── main.py           # FastAPI主入口 (端口8000)
│   ├── api/chat.py       # 聊天API路由 (同步/流式/历史)
│   ├── core/
│   │   ├── llm.py        # 小米Mimo API封装
│   │   ├── agent.py      # Agent核心 (多轮对话+RAG)
│   │   ├── knowledge_loader.py  # 知识库加载与向量化
│   │   ├── cache.py      # 模型缓存+检索LRU缓存
│   │   └── conversation.py  # 对话历史管理 (JSON持久化)
│   └── frontend/
│       ├── index.html    # 自定义Web前端
│       └── app.py        # Gradio备用界面 (端口7860)
└── docs/                 # 开发文档
```

## Quick Start
```bash
# 1. 配置API Key
cp config/.env.example config/.env
# 编辑 config/.env 填入 XIAOMI_API_KEY

# 2. 安装依赖
pip install -r requirements.txt

# 3. 构建知识库 (首次)
python src/core/knowledge_loader.py

# 4. 启动服务
python src/main.py
# 访问 http://127.0.0.1:8000
```

## Documentation
- 开发文档: `docs/开发文档-校园答疑智能客服AI Agent.html`
- 技术路线图: `docs/技术路线图-校园答疑智能客服AI Agent.html`
- 优化方案: `docs/项目优化方案.md`
- 对比分析: `docs/项目对比分析.md`

## Development Mode
User is a beginner (小白), building from scratch. Follow the step-by-step guide in the development docs.
