# 校园答疑智能客服 AI Agent 开发文档

## 一、项目概述

### 1.1 项目目标
构建一个基于大语言模型（LLM）的校园答疑智能客服系统，能够回答学生关于校园生活、教务管理、选课、考试、图书馆、食堂、宿舍等方面的常见问题。系统采用轻量化部署方案，降低硬件要求，方便本地化运行。

### 1.2 核心功能
- **智能问答**：基于校园知识库回答学生问题
- **多轮对话**：支持上下文理解，连续对话
- **知识检索增强**：结合检索增强生成（RAG）技术，提升回答准确性
- **意图识别**：识别学生问题属于哪个类别（教务、生活、设施等）
- **多渠道接入**：支持 Web 页面、微信公众号等前端入口

### 1.3 技术特色
- 轻量化部署：使用小参数量模型或 API 调用方式
- 低门槛：适合个人开发者或小团队
- 可扩展：知识库可灵活更新

---

## 二、技术路线

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端展示层                            │
│    Web 界面 (Gradio/Streamlit) │ 微信公众号 │ 小程序        │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/WebSocket
┌────────────────────────▼────────────────────────────────────┐
│                      后端服务层 (FastAPI)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 意图识别  │  │ 对话管理  │  │ 知识检索  │  │ 回答生成  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                      数据与模型层                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  向量数据库   │  │  知识库文档   │  │   大语言模型      │  │
│  │ (ChromaDB)   │  │ (校园FAQ等)  │  │ (本地/API调用)    │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 技术选型

| 组件 | 技术方案 | 说明 |
|------|----------|------|
| **编程语言** | Python 3.10+ | 生态完善，AI 库支持好 |
| **Web 框架** | FastAPI | 高性能异步框架，自带 API 文档 |
| **前端界面** | Gradio 或 Streamlit | 快速搭建，适合原型开发 |
| **大语言模型** | Qwen2.5-7B / ChatGLM3-6B / DeepSeek API | 国产开源模型，中文能力强 |
| **向量数据库** | ChromaDB | 轻量级，无需额外部署 |
| **Embedding 模型** | BGE-large-zh 或 text-embedding-v3 | 中文语义向量化 |
| **Prompt 框架** | LangChain | 统一管理 RAG 流程 |
| **文档解析** | PyPDF2 / python-docx | 解析校园文档 |

### 2.3 两种部署模式

#### 模式 A：本地部署（推荐学习）
适合有 GPU 显卡（8GB+显存）或想学习本地部署的用户：
- 使用 Ollama + Qwen2.5-7B-Chinese
- 优点：数据安全、无 API 费用
- 缺点：需要 GPU 硬件

#### 模式 B：API 调用（推荐快速上手）
适合没有 GPU 的用户：
- 调用 DeepSeek / 通义千问 / 智谱 API
- 优点：零硬件要求、快速启动
- 缺点：有 API 调用费用、依赖网络

---

## 三、开发条件

### 3.1 硬件要求

#### 模式 A 本地部署
| 配置项 | 最低要求 | 推荐配置 |
|--------|----------|----------|
| CPU | Intel i5 / AMD R5 | Intel i7 / AMD R7 |
| 内存 | 8GB | 16GB+ |
| GPU | NVIDIA 8GB 显存 | NVIDIA 16GB+ 显存 |
| 硬盘 | 20GB 可用空间 | 50GB+ SSD |

#### 模式 B API 调用
| 配置项 | 要求 |
|--------|------|
| CPU | 任意 |
| 内存 | 4GB+ |
| GPU | 不需要 |
| 硬盘 | 10GB 可用空间 |
| 网络 | 需要互联网连接 |

### 3.2 软件环境

| 软件 | 版本 | 用途 |
|------|------|------|
| Python | 3.10 或 3.11 | 运行环境 |
| pip | 最新版 | 包管理 |
| Git | 最新版 | 版本控制 |
| VS Code | 最新版 | 代码编辑器 |
| Ollama（可选） | 最新版 | 本地运行大模型 |
| CUDA（可选） | 12.x | GPU 加速 |

### 3.3 API 申请（模式 B）
如果选择 API 调用模式，需要申请以下 API：
- **DeepSeek API**：https://platform.deepseek.com/ （注册送 500 万 token 免费额度）
- **通义千问 API**：https://dashscope.aliyun.com/ （注册送免费额度）
- **智谱 API**：https://open.bigmodel.cn/ （注册送免费额度）

---

## 四、项目结构

```
campus-qa-bot/
├── docs/                        # 开发文档
│   └── README.md
├── config/                      # 配置文件
│   ├── config.yaml              # 主配置
│   └── .env                     # 环境变量（API Key等）
├── knowledge_base/              # 知识库
│   ├── faq/                     # FAQ 文档
│   │   ├── 教务管理.md
│   │   ├── 校园生活.md
│   │   ├── 图书馆.md
│   │   ├── 选课指南.md
│   │   └── 考试安排.md
│   └── processed/               # 向量化后的数据
├── src/                         # 源代码
│   ├── main.py                  # FastAPI 主入口
│   ├── config.py                # 配置加载
│   ├── api/                     # API 路由
│   │   └── chat.py
│   ├── core/                    # 核心模块
│   │   ├── llm.py              # 大模型封装
│   │   ├── retriever.py        # 知识检索
│   │   ├── agent.py            # Agent 逻辑
│   │   └── knowledge_loader.py # 知识库加载
│   ├── utils/                   # 工具函数
│   │   ├── document_parser.py  # 文档解析
│   │   └── text_splitter.py    # 文本分块
│   └── frontend/               # 前端页面
│       └── app.py
├── tests/                       # 测试
├── scripts/                     # 脚本
│   ├── build_kb.py             # 构建知识库
│   └── start.sh                # 启动脚本
├── requirements.txt             # 依赖列表
└── README.md
```

---

## 五、开发步骤（分阶段）

### 阶段一：环境搭建（第 1 天）

#### 步骤 1：安装 Python 环境
```bash
# 下载并安装 Python 3.11
# Windows: https://www.python.org/downloads/
# 安装时勾选 "Add Python to PATH"

# 验证安装
python --version
pip --version
```

#### 步骤 2：创建项目目录
```bash
# 创建项目文件夹
mkdir campus-qa-bot
cd campus-qa-bot

# 创建子目录
mkdir -p config knowledge_base/faq knowledge_base/processed src/api src/core src/utils src/frontend tests scripts docs
```

#### 步骤 3：创建虚拟环境
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 升级 pip
pip install --upgrade pip
```

#### 步骤 4：安装基础依赖
```bash
# 创建 requirements.txt
pip install fastapi uvicorn python-dotenv pyyaml requests

# 保存依赖
pip freeze > requirements.txt
```

---

### 阶段二：构建知识库（第 2-3 天）

#### 步骤 1：准备 FAQ 知识库文档

在 `knowledge_base/faq/` 目录下创建 Markdown 文件，内容示例：

**教务管理.md**:
```markdown
# 教务管理常见问题

## 选课
- Q: 什么时候可以选课？
  A: 每学期选课分为三个阶段：预选（开学前两周）、正选（开学第一周）、补退选（开学第二周）。具体时间请关注教务处通知。

- Q: 选课系统在哪里登录？
  A: 登录学校教务管理系统 https://jwxt.xxx.edu.cn，使用学号和密码登录。

## 成绩查询
- Q: 如何查询成绩？
  A: 登录教务系统，在"成绩查询"模块可以查看各学期成绩。期末考试结束后约两周可查询。

- Q: 成绩有误怎么办？
  A: 如发现成绩有误，请在开学后一周内向所在学院教务办提交成绩复核申请。
```

**校园生活.md**:
```markdown
# 校园生活常见问题

## 食堂
- Q: 食堂几点开门？
  A: 早餐 6:30-9:00，午餐 11:00-13:00，晚餐 17:00-19:30。

- Q: 食堂支持哪些支付方式？
  A: 支持校园卡、微信支付、支付宝支付。

## 宿舍
- Q: 宿舍断电时间是？
  A: 周日到周四晚 23:00 断电，周五周六晚 24:00 断电。空调和独立卫生间供电不受影响。

- Q: 如何报修宿舍设施？
  A: 通过"智慧校园"App 提交报修申请，或联系宿管阿姨登记。
```

#### 步骤 2：编写文档解析与加载模块

后续将编写 `knowledge_loader.py` 来：
1. 读取 Markdown 文件
2. 将文档按段落/问答对拆分成小块
3. 使用 Embedding 模型将文本转为向量
4. 存入 ChromaDB 向量数据库

---

### 阶段三：搭建大模型接口（第 3-4 天）

#### 方案 A：本地 Ollama 部署

**步骤 1：安装 Ollama**
```bash
# 下载 Ollama: https://ollama.com/download
# 安装后在终端运行：
ollama pull qwen2.5:7b

# 测试运行
ollama run qwen2.5:7b
```

**步骤 2：编写 LLM 封装模块** (`src/core/llm.py`)
- 封装 Ollama API 调用
- 统一接口，方便后续切换模型

#### 方案 B：API 调用

**步骤 1：获取 API Key**
- 注册 DeepSeek 开放平台账号
- 获取 API Key

**步骤 2：配置环境变量**
创建 `config/.env`:
```
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
```

**步骤 3：编写 LLM 封装模块**
- 封装 DeepSeek API 调用
- 支持流式输出

---

### 阶段四：实现 RAG 检索增强（第 4-5 天）

#### 步骤 1：安装向量数据库和 Embedding 模型
```bash
pip install chromadb sentence-transformers
```

#### 步骤 2：编写检索模块 (`src/core/retriever.py`)
- 接收用户问题
- 使用 Embedding 模型将问题转为向量
- 在 ChromaDB 中检索最相关的 Top-K 知识片段
- 返回检索结果

#### 步骤 3：编写 Prompt 模板
```python
prompt_template = """你是一个校园答疑助手。请根据以下参考资料回答学生的问题。
如果参考资料中没有相关信息，请诚实地说"抱歉，我没有找到相关信息，建议您联系学校相关部门咨询"。

参考资料：
{context}

学生问题：{question}

请用友好、简洁的语言回答："""
```

---

### 阶段五：编写 Agent 核心逻辑（第 5-6 天）

#### 步骤 1：编写 Agent 模块 (`src/core/agent.py`)
- 接收用户输入
- 调用检索器获取相关知识
- 构建 Prompt（问题 + 知识）
- 调用 LLM 生成回答
- 返回结果

#### 步骤 2：设计多轮对话管理
- 使用消息历史列表记录对话
- 控制上下文窗口长度（避免超长）
- 支持会话 ID 区分不同用户

---

### 阶段六：搭建 Web API（第 6-7 天）

#### 步骤 1：创建 FastAPI 服务 (`src/main.py`)
```python
# 基本 API 结构
POST /api/chat          # 发送消息，获取回复（流式/非流式）
GET  /api/health        # 健康检查
GET  /api/history/{id}  # 获取对话历史
```

#### 步骤 2：添加 CORS 中间件
- 允许前端跨域请求

#### 步骤 3：编写前端页面 (`src/frontend/app.py`)
- 使用 Gradio 搭建聊天界面
- 支持 Markdown 渲染
- 支持流式显示回答

---

### 阶段七：测试与优化（第 7-8 天）

#### 步骤 1：功能测试
- 测试各类问题的回答准确性
- 测试边界情况（空问题、超长问题、无关问题）

#### 步骤 2：性能优化
- 优化检索速度
- 优化 Prompt，减少 token 消耗
- 添加回答缓存

#### 步骤 3：用户体验优化
- 添加"加载中"提示
- 优化回答格式
- 添加反馈功能（点赞/点踩）

---

### 阶段八：部署上线（第 8-10 天）

#### 方案 1：本地部署
```bash
# 启动后端服务
uvicorn src.main:app --host 0.0.0.0 --port 8000

# 启动前端界面
python src/frontend/app.py
```

#### 方案 2：Docker 部署
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 方案 3：云服务器部署
- 购买轻量云服务器（如阿里云、腾讯云）
- 部署到服务器
- 配置域名和 HTTPS

---

## 六、关键技术详解

### 6.1 RAG（检索增强生成）原理

```
用户提问 → Embedding → 向量检索 → Top-K 文档片段
                                      ↓
                                   Prompt 组装
                                      ↓
                              LLM 生成回答 → 返回用户
```

### 6.2 文本分块策略

- **按问答对分块**：每对 Q&A 作为一个 chunk（推荐）
- **按段落分块**：每 200-500 字为一个 chunk
- **重叠窗口**：相邻 chunk 重叠 50-100 字，避免信息断裂

### 6.3 Prompt 工程

关键要素：
1. **角色设定**：明确 AI 助手身份
2. **参考资料**：注入检索到的知识片段
3. **回答约束**：要求基于参考资料回答，不编造
4. **格式要求**：简洁友好的语言风格

---

## 七、常见问题与解决

| 问题 | 解决方案 |
|------|----------|
| 模型回答不准确 | 优化 Prompt，增加检索数量，检查知识库内容 |
| 检索速度慢 | 优化 Embedding 模型，使用更小的模型，增加硬件 |
| 中文乱码 | 确保文件编码为 UTF-8 |
| API 调用失败 | 检查网络和 API Key 是否正确 |
| 内存不足 | 使用更小的模型，或切换为 API 调用模式 |

---

## 八、项目时间规划

| 阶段 | 内容 | 预计时间 |
|------|------|----------|
| 阶段一 | 环境搭建 | 第 1 天 |
| 阶段二 | 知识库构建 | 第 2-3 天 |
| 阶段三 | 大模型接口 | 第 3-4 天 |
| 阶段四 | RAG 检索增强 | 第 4-5 天 |
| 阶段五 | Agent 核心 | 第 5-6 天 |
| 阶段六 | Web API 与前端 | 第 6-7 天 |
| 阶段七 | 测试优化 | 第 7-8 天 |
| 阶段八 | 部署上线 | 第 8-10 天 |

**总周期：约 10 天**（每天投入 3-4 小时）

---

## 九、后续可扩展方向

1. **接入微信公众号**：使用 WeChat API 实现微信端问答
2. **语音交互**：集成语音识别（ASR）和语音合成（TTS）
3. **图片理解**：支持学生上传课表、通知等图片进行识别
4. **多语言支持**：支持英文、日文等外语问答
5. **数据分析**：统计高频问题，优化知识库
6. **个性化推荐**：根据学生专业、年级推荐相关课程信息

---

## 十、参考资源

- LangChain 中文文档：https://python.langchain.com/
- ChromaDB 文档：https://docs.trychroma.com/
- Ollama 官网：https://ollama.com/
- DeepSeek API 文档：https://platform.deepseek.com/api-docs
- Gradio 文档：https://www.gradio.app/docs
