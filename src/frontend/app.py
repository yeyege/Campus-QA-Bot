"""
校园答疑智能客服 - Gradio前端（多轮对话版）
"""
import os
import sys
import uuid

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import gradio as gr
from src.core.agent import CampusAgent

print("正在初始化校园答疑助手...")
agent = CampusAgent()
print("初始化完成！")


def chat(message, history, session_id):
    """多轮对话聊天函数"""
    if history is None:
        history = []

    # 复制历史，避免修改原始数据
    history = history.copy()

    # 添加用户消息
    history.append({"role": "user", "content": message})

    try:
        # 流式输出
        response = ""
        for chunk in agent.chat_stream(message, session_id):
            response += chunk
            # 返回当前状态
            current_history = history.copy()
            current_history.append({"role": "assistant", "content": response})
            yield current_history
    except Exception as e:
        error_history = history.copy()
        error_history.append({"role": "assistant", "content": f"抱歉，处理您的问题时出现错误：{str(e)}"})
        yield error_history


def new_chat():
    return [], str(uuid.uuid4())


def clear_history(session_id):
    agent.clear_history(session_id)
    return [], session_id


def create_demo():
    with gr.Blocks(title="校园答疑智能客服") as demo:
        session_id = gr.State(value=str(uuid.uuid4()))

        gr.HTML("""
        <div style="background: #0f0f0f; padding: 12px 25px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 22px;">🎓</span>
                <span style="font-size: 18px; font-weight: 600; color: #fff;">校园答疑智能客服</span>
            </div>
            <div style="display: flex; align-items: center; gap: 15px;">
                <span style="font-size: 13px; color: #888;">多轮对话 · RAG检索</span>
                <div style="width: 8px; height: 8px; background: #22c55e; border-radius: 50%;"></div>
            </div>
        </div>
        """)

        with gr.Row():
            with gr.Column(scale=1, min_width=220):
                gr.HTML("""<div style="color: #fff; font-size: 16px; font-weight: 600; margin-bottom: 15px;">🎓 校园助手</div>""")
                new_btn = gr.Button("+ 新建对话", variant="secondary")

            with gr.Column(scale=3):
                chatbot = gr.Chatbot(label="", height=450, type="messages")

                with gr.Row():
                    msg = gr.Textbox(
                        label="",
                        placeholder="输入你的问题... (支持多轮对话)",
                        lines=1,
                        scale=4,
                        show_label=False
                    )
                    submit_btn = gr.Button("发送", variant="primary", scale=1)

                gr.HTML("""<div style="color: #888; font-size: 12px; margin: 10px 0;">💡 试试这些问题：</div>""")
                with gr.Row():
                    examples = ["食堂几点开门？", "选课系统在哪里？", "如何查询成绩？", "图书馆借多少本书？"]
                    for ex in examples:
                        btn = gr.Button(ex, variant="secondary", size="sm")
                        btn.click(lambda x=ex: x, outputs=[msg])

            with gr.Column(scale=1, min_width=180):
                gr.HTML("""
                <div style="color: #888; font-size: 13px; margin-bottom: 15px;">📚 知识库</div>
                <div style="color: #e0e0e0; font-size: 14px;">42 条FAQ</div>
                <div style="color: #666; font-size: 12px; margin-top: 5px;">教务·生活·图书馆</div>

                <div style="color: #888; font-size: 13px; margin-top: 25px; margin-bottom: 10px;">🎯 特性</div>
                <div style="color: #e0e0e0; font-size: 12px; line-height: 1.8;">
                    ✓ 多轮对话<br>
                    ✓ 上下文理解<br>
                    ✓ 知识库检索<br>
                    ✓ 流式输出
                </div>
                """)

        gr.HTML("""
        <div style="background: #0f0f0f; padding: 10px; text-align: center; border-top: 1px solid #333; margin-top: 20px;">
            <span style="font-size: 12px; color: #666;">校园答疑智能客服 | RAG + 小米Mimo</span>
        </div>
        """)

        # 绑定事件
        submit_btn.click(
            chat,
            inputs=[msg, chatbot, session_id],
            outputs=[chatbot]
        )

        msg.submit(
            chat,
            inputs=[msg, chatbot, session_id],
            outputs=[chatbot]
        )

        new_btn.click(
            new_chat,
            outputs=[chatbot, session_id]
        )

    return demo


if __name__ == "__main__":
    demo = create_demo()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True
    )
