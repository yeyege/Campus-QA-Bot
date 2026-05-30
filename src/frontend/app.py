"""
校园答疑智能客服 - Gradio前端界面
对标DeepSeek风格
"""
import os
import sys

# 设置环境变量
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import gradio as gr
from src.core.agent import CampusAgent

# 初始化Agent
print("正在初始化校园答疑助手...")
agent = CampusAgent()
print("初始化完成！")


def chat(message, history):
    """聊天函数"""
    if history is None:
        history = []

    # 添加用户消息
    history.append({"role": "user", "content": message})

    try:
        # 流式输出
        response = ""
        for chunk in agent.chat_stream(message):
            response += chunk
            yield history + [{"role": "assistant", "content": response}]
    except Exception as e:
        yield history + [{"role": "assistant", "content": f"抱歉，处理您的问题时出现错误：{str(e)}"}]


def clear_history():
    """清空历史"""
    return [], ""


# 自定义CSS - DeepSeek风格
custom_css = """
/* 全局样式 */
.gradio-container {
    max-width: 100% !important;
    padding: 0 !important;
}

/* 主容器 */
.main-container {
    display: flex;
    height: 100vh;
    overflow: hidden;
}

/* 左侧边栏 */
.sidebar {
    width: 260px;
    background: #1e1e1e;
    color: #fff;
    padding: 20px;
    display: flex;
    flex-direction: column;
    border-right: 1px solid #333;
}

.sidebar-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #333;
    display: flex;
    align-items: center;
    gap: 10px;
}

.new-chat-btn {
    background: #2d2d2d !important;
    color: #fff !important;
    border: 1px solid #444 !important;
    border-radius: 8px !important;
    padding: 12px !important;
    margin-bottom: 20px !important;
    cursor: pointer;
    transition: all 0.2s;
}

.new-chat-btn:hover {
    background: #3d3d3d !important;
    border-color: #666 !important;
}

/* 主聊天区域 */
.chat-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #1e1e1e;
}

/* 聊天头部 */
.chat-header {
    padding: 15px 25px;
    border-bottom: 1px solid #333;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.chat-title {
    font-size: 16px;
    font-weight: 500;
    color: #fff;
}

/* 消息区域 */
.messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 20px 25px;
}

/* 消息样式 */
.message {
    max-width: 800px;
    margin: 0 auto 20px;
    padding: 15px 20px;
    border-radius: 12px;
    line-height: 1.6;
}

.user-message {
    background: #2563eb;
    color: #fff;
    margin-left: auto;
    border-bottom-right-radius: 4px;
}

.assistant-message {
    background: #2d2d2d;
    color: #e0e0e0;
    border-bottom-left-radius: 4px;
}

/* 输入区域 */
.input-area {
    padding: 20px 25px;
    background: #1e1e1e;
    border-top: 1px solid #333;
}

.input-wrapper {
    max-width: 800px;
    margin: 0 auto;
    position: relative;
}

.input-box {
    width: 100%;
    min-height: 50px;
    max-height: 150px;
    padding: 12px 50px 12px 16px;
    background: #2d2d2d;
    border: 1px solid #444;
    border-radius: 12px;
    color: #fff;
    font-size: 15px;
    resize: none;
    outline: none;
    transition: border-color 0.2s;
}

.input-box:focus {
    border-color: #2563eb;
}

.send-btn {
    position: absolute;
    right: 10px;
    bottom: 10px;
    width: 36px;
    height: 36px;
    background: #2563eb !important;
    border: none !important;
    border-radius: 8px !important;
    color: #fff !important;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s;
}

.send-btn:hover {
    background: #1d4ed8 !important;
}

.send-btn:disabled {
    background: #444 !important;
    cursor: not-allowed;
}

/* 右侧示例区域 */
.examples-panel {
    width: 280px;
    background: #1e1e1e;
    padding: 20px;
    border-left: 1px solid #333;
    overflow-y: auto;
}

.examples-title {
    font-size: 14px;
    font-weight: 500;
    color: #888;
    margin-bottom: 15px;
}

.example-item {
    padding: 12px 15px;
    background: #2d2d2d;
    border-radius: 8px;
    margin-bottom: 10px;
    cursor: pointer;
    color: #e0e0e0;
    font-size: 14px;
    transition: all 0.2s;
    border: 1px solid transparent;
}

.example-item:hover {
    background: #3d3d3d;
    border-color: #2563eb;
}

/* Chatbot组件样式覆盖 */
.gradio-chatbot {
    background: transparent !important;
    border: none !important;
}

.gradio-chatbot .message {
    max-width: 800px !important;
    margin: 0 auto 15px !important;
}

/* 隐藏默认组件 */
.gradio-container .sidebar,
.gradio-container .examples-panel {
    display: none;
}

/* 响应式设计 */
@media (max-width: 1200px) {
    .examples-panel {
        display: none;
    }
}

@media (max-width: 768px) {
    .sidebar {
        display: none;
    }
}
"""

# DeepSeek风格的HTML模板
html_template = """
<div style="display: flex; height: 100vh; background: #1e1e1e;">
    <!-- 左侧边栏 -->
    <div style="width: 260px; background: #1e1e1e; color: #fff; padding: 20px; border-right: 1px solid #333; display: flex; flex-direction: column;">
        <div style="font-size: 18px; font-weight: 600; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #333;">
            🎓 校园答疑助手
        </div>
        <button onclick="clearChat()" style="background: #2d2d2d; color: #fff; border: 1px solid #444; border-radius: 8px; padding: 12px; cursor: pointer; margin-bottom: 20px;">
            + 新建对话
        </button>
        <div style="flex: 1; overflow-y: auto;">
            <div style="padding: 10px; background: #2d2d2d; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #2563eb;">
                当前对话
            </div>
        </div>
        <div style="padding-top: 15px; border-top: 1px solid #333; font-size: 12px; color: #666;">
            基于RAG的校园答疑系统
        </div>
    </div>

    <!-- 主聊天区域 -->
    <div style="flex: 1; display: flex; flex-direction: column;">
        <div style="padding: 15px 25px; border-bottom: 1px solid #333; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 16px; color: #fff;">对话</span>
            <span style="font-size: 12px; color: #666;">校园知识库 · 42条FAQ</span>
        </div>
    </div>

    <!-- 右侧示例 -->
    <div style="width: 280px; background: #1e1e1e; padding: 20px; border-left: 1px solid #333;">
        <div style="font-size: 14px; color: #888; margin-bottom: 15px;">试试这些问题</div>
        <div onclick="setQuestion('食堂几点开门？')" style="padding: 12px; background: #2d2d2d; border-radius: 8px; margin-bottom: 10px; cursor: pointer; color: #e0e0e0; font-size: 14px;">食堂几点开门？</div>
        <div onclick="setQuestion('选课系统在哪里登录？')" style="padding: 12px; background: #2d2d2d; border-radius: 8px; margin-bottom: 10px; cursor: pointer; color: #e0e0e0; font-size: 14px;">选课系统在哪里登录？</div>
        <div onclick="setQuestion('如何查询成绩？')" style="padding: 12px; background: #2d2d2d; border-radius: 8px; margin-bottom: 10px; cursor: pointer; color: #e0e0e0; font-size: 14px;">如何查询成绩？</div>
        <div onclick="setQuestion('图书馆可以借多少本书？')" style="padding: 12px; background: #2d2d2d; border-radius: 8px; margin-bottom: 10px; cursor: pointer; color: #e0e0e0; font-size: 14px;">图书馆可以借多少本书？</div>
        <div onclick="setQuestion('宿舍断电时间是？')" style="padding: 12px; background: #2d2d2d; border-radius: 8px; margin-bottom: 10px; cursor: pointer; color: #e0e0e0; font-size: 14px;">宿舍断电时间是？</div>
        <div onclick="setQuestion('心理咨询怎么预约？')" style="padding: 12px; background: #2d2d2d; border-radius: 8px; margin-bottom: 10px; cursor: pointer; color: #e0e0e0; font-size: 14px;">心理咨询怎么预约？</div>
    </div>
</div>

<script>
function setQuestion(q) {
    document.querySelector('textarea').value = q;
    document.querySelector('textarea').dispatchEvent(new Event('input'));
}
function clearChat() {
    document.querySelector('button[aria-label="Clear"]').click();
}
</script>
"""


def create_demo():
    """创建Gradio界面"""
    with gr.Blocks(title="校园答疑智能客服") as demo:
        # 顶部导航栏
        gr.HTML("""
        <div style="background: #0f0f0f; padding: 12px 25px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 22px;">🎓</span>
                <span style="font-size: 18px; font-weight: 600; color: #fff;">校园答疑智能客服</span>
            </div>
            <div style="display: flex; align-items: center; gap: 15px;">
                <span style="font-size: 13px; color: #888;">基于 RAG + 大语言模型</span>
                <div style="width: 8px; height: 8px; background: #22c55e; border-radius: 50%;"></div>
            </div>
        </div>
        """)

        with gr.Row(elem_classes="main-container"):
            # 左侧边栏
            with gr.Column(scale=1, min_width=260, elem_classes="sidebar"):
                gr.HTML("""
                <div class="sidebar-title">🎓 校园答疑助手</div>
                <button class="new-chat-btn" onclick="clearChat()">+ 新建对话</button>
                <div style="flex: 1;">
                    <div style="padding: 10px; background: #2d2d2d; border-radius: 8px; border-left: 3px solid #2563eb;">
                        💬 当前对话
                    </div>
                </div>
                <div style="padding-top: 15px; border-top: 1px solid #333; font-size: 12px; color: #666;">
                    基于RAG的校园答疑系统
                </div>
                """)

            # 中间聊天区域
            with gr.Column(scale=3, elem_classes="chat-area"):
                chatbot = gr.Chatbot(
                    label="",
                    height=500
                )

                with gr.Row(elem_classes="input-area"):
                    with gr.Column(scale=4):
                        msg = gr.Textbox(
                            label="",
                            placeholder="输入你的问题... (Shift+Enter换行)",
                            lines=1,
                            max_lines=5,
                            show_label=False,
                            container=False
                        )
                    with gr.Column(scale=0, min_width=60):
                        submit_btn = gr.Button("发送", variant="primary", size="lg")

            # 右侧示例
            with gr.Column(scale=1, min_width=280, elem_classes="examples-panel"):
                gr.HTML("""
                <div class="examples-title">💡 试试这些问题</div>
                """)
                examples = [
                    "食堂几点开门？",
                    "选课系统在哪里登录？",
                    "如何查询成绩？",
                    "图书馆可以借多少本书？",
                    "宿舍断电时间是？",
                    "心理咨询怎么预约？",
                    "校园网怎么连接？",
                    "如何报修宿舍设施？"
                ]
                for ex in examples:
                    btn = gr.Button(ex, variant="secondary", size="sm")
                    btn.click(
                        lambda x=ex: x,
                        outputs=msg
                    )

                gr.HTML("""
                <div style="margin-top: 20px; padding: 15px; background: #2d2d2d; border-radius: 8px;">
                    <div style="font-size: 13px; color: #888; margin-bottom: 10px;">📚 知识库统计</div>
                    <div style="font-size: 14px; color: #e0e0e0;">42 条常见问答</div>
                    <div style="font-size: 12px; color: #666; margin-top: 5px;">教务管理 · 校园生活 · 图书馆</div>
                </div>
                """)

        # 页脚
        gr.HTML("""
        <div style="background: #0f0f0f; padding: 10px 25px; text-align: center; border-top: 1px solid #333;">
            <span style="font-size: 12px; color: #666;">校园答疑智能客服 © 2024 | 基于 RAG + 小米Mimo 大语言模型</span>
        </div>
        """)

        # 绑定事件
        submit_btn.click(
            chat,
            inputs=[msg, chatbot],
            outputs=[chatbot]
        )
        msg.submit(
            chat,
            inputs=[msg, chatbot],
            outputs=[chatbot]
        )

    return demo


if __name__ == "__main__":
    demo = create_demo()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        css=custom_css
    )
