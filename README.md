# Campus QA Bot - 校园答疑智能客服

基于大语言模型的校园答疑系统，采用 RAG（检索增强生成）技术，通过 API 调用云端大模型实现智能问答。

## 功能特性

- 多轮对话：支持上下文关联的连续对话
- 流式输出：实时返回回复内容，类似 ChatGPT 打字效果
- 知识检索：基于 ChromaDB + BGE 向量模型的语义检索
- 会话管理：自动保存/清除对话历史

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| 大模型 | Xiaomi MiMo API |
| 向量数据库 | ChromaDB |
| Embedding | BGE-small-zh-v1.5 |
| 前端 | 原生 HTML + JavaScript |

## 项目结构

```
campus-qa-bot/
├── config/                  # 配置文件（.env）
├── knowledge_base/
│   ├── faq/                 # FAQ 知识库（Markdown 格式）
│   └── processed/           # ChromaDB 向量数据
├── src/
│   ├── api/chat.py          # FastAPI 路由（同步 + 流式）
│   ├── core/
│   │   ├── agent.py         # Agent 核心逻辑
│   │   ├── llm.py           # 大模型 API 封装
│   │   ├── knowledge_loader.py  # 知识库加载与检索
│   │   ├── conversation.py  # 对话历史管理
│   │   └── cache.py         # 模型缓存
│   ├── frontend/            # 前端页面
│   └── main.py              # 启动入口
└── docs/                    # 开发文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install fastapi uvicorn chromadb sentence-transformers requests python-dotenv
```

### 2. 配置环境变量

在 `config/.env` 中填写：

```env
LLM_PROVIDER=xiaomi
XIAOMI_API_KEY=你的API密钥
XIAOMI_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
XIAOMI_MODEL=mimo-v2.5
LLM_MAX_TOKENS=256
LLM_TEMPERATURE=0.5
```

### 3. 构建知识库

```bash
python -m src.core.knowledge_loader
```

### 4. 启动服务

```bash
python src/main.py
```

访问 http://127.0.0.1:8000 打开前端页面。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat` | 同步聊天 |
| POST | `/api/chat/stream` | 流式聊天（SSE） |
| GET | `/api/history/{session_id}` | 获取对话历史 |
| DELETE | `/api/history/{session_id}` | 清除对话历史 |
| GET | `/api/health` | 健康检查 |

## 开发文档

- [开发文档](docs/开发文档-校园答疑智能客服AI Agent.md)
- [技术路线图](docs/技术路线图-校园答疑智能客服AI Agent.md)
