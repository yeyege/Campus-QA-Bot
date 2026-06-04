# -*- coding: utf-8 -*-
"""
校园答疑智能客服 - Gradio前端（三栏布局）
"""
import os
import sys
import uuid
import json

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import gradio as gr
from src.core.agent import CampusAgent

print("正在初始化校园答疑助手...")
agent = CampusAgent()
print("初始化完成！")

# ============================================================
# CSS 样式
# ============================================================
CUSTOM_CSS = """
/* ===== 全局 ===== */
.gradio-container { max-width: 100% !important; margin: 0 !important; padding: 0 !important; }
body { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }

/* ===== 顶部导航 ===== */
.top-nav {
    display: flex; align-items: center; height: 48px;
    background: #fff; border-bottom: 1px solid #e5e7eb; padding: 0 20px;
}
.top-nav .logo { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 700; color: #333; }
.top-nav .logo svg { width: 24px; height: 24px; fill: #4f8cff; }
.top-nav nav { display: flex; gap: 24px; margin-left: 40px; }
.top-nav nav a { color: #6b7280; text-decoration: none; font-size: 14px; cursor: pointer; }
.top-nav nav a:hover, .top-nav nav a.active { color: #333; font-weight: 500; }

/* ===== 左侧栏 ===== */
.left-sidebar {
    background: #fff; border-right: 1px solid #e5e7eb;
    padding: 16px 12px; height: 100%; display: flex; flex-direction: column;
}
.sidebar-label { color: #6b7280; font-size: 11px; font-weight: 500; text-transform: uppercase; margin-bottom: 4px; }
.menu-item {
    display: flex; align-items: center; gap: 8px;
    padding: 10px 12px; border-radius: 6px; cursor: pointer;
    color: #333; font-size: 14px; margin-bottom: 2px; transition: background 0.15s;
}
.menu-item:hover { background: #f3f4f6; }
.menu-item.active { background: #eff6ff; color: #3b82f6; font-weight: 500; }
.menu-item svg { width: 18px; height: 18px; flex-shrink: 0; }

/* ===== 会话列表栏 ===== */
.session-panel {
    background: #fafbfc; border-right: 1px solid #e5e7eb;
    display: flex; flex-direction: column; height: 100%;
}
.session-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 16px; border-bottom: 1px solid #e5e7eb;
}
.session-header h3 { margin: 0; font-size: 15px; font-weight: 600; color: #111827; }
.session-header-btns { display: flex; gap: 6px; }
.session-header-btns button {
    background: none; border: none; cursor: pointer; padding: 4px; border-radius: 4px;
    display: flex; align-items: center; justify-content: center; color: #6b7280;
}
.session-header-btns button:hover { background: #e5e7eb; color: #333; }

.session-search { padding: 8px 16px; border-bottom: 1px solid #e5e7eb; }
.session-search input {
    width: 100%; padding: 8px 12px; border: 1px solid #e5e7eb; border-radius: 6px;
    font-size: 13px; outline: none; background: #fff; box-sizing: border-box;
}
.session-search input:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59,130,246,0.1); }

.session-list { flex: 1; overflow-y: auto; padding: 8px; }
.session-item {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 12px; border-radius: 6px; cursor: pointer;
    margin-bottom: 2px; transition: background 0.15s;
}
.session-item:hover { background: #f3f4f6; }
.session-item.active { background: #eff6ff; }
.session-item-title { font-size: 13px; color: #333; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 160px; }
.session-item-time { font-size: 11px; color: #9ca3af; margin-top: 2px; }
.session-item-more {
    background: none; border: none; cursor: pointer; padding: 2px 4px;
    border-radius: 4px; color: #9ca3af; font-size: 16px; line-height: 1;
}
.session-item-more:hover { background: #e5e7eb; color: #333; }

/* Session Dropdown Override */
.session-dropdown-wrap { padding: 8px; border-bottom: 1px solid #e5e7eb; }
.session-dropdown-wrap label { display: none !important; }
.session-dropdown-wrap .wrap-inner { background: transparent !important; border: none !important; padding: 0 !important; }
.session-dropdown-wrap .wrap-inner .secondary-wrap { display: none !important; }
.session-dropdown-wrap input[type="text"],
.session-dropdown-wrap select {
    width: 100% !important; padding: 8px 12px !important;
    border: 1px solid #e5e7eb !important; border-radius: 6px !important;
    font-size: 13px !important; background: #fff !important; outline: none !important;
    box-sizing: border-box !important;
}

/* ===== 聊天区 ===== */
.chat-area { background: #fff; display: flex; flex-direction: column; height: 100%; }
.chat-header {
    display: flex; align-items: center; gap: 10px;
    padding: 12px 20px; border-bottom: 1px solid #e5e7eb;
}
.chat-header .avatar {
    width: 32px; height: 32px; border-radius: 50%; background: #3b82f6;
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-size: 14px; font-weight: 600;
}
.chat-header .info .name { font-size: 14px; font-weight: 600; color: #111827; }
.chat-header .info .time { font-size: 11px; color: #9ca3af; }

.chat-messages { flex: 1; overflow-y: auto; padding: 20px; }

/* 消息气泡 */
.msg { display: flex; gap: 8px; margin-bottom: 16px; max-width: 70%; }
.msg.user { flex-direction: row-reverse; margin-left: auto; }
.msg.assistant { flex-direction: row; }
.msg-avatar {
    width: 32px; height: 32px; border-radius: 50%; display: flex;
    align-items: center; justify-content: center; flex-shrink: 0;
    font-size: 13px; font-weight: 600; color: #fff;
}
.msg.user .msg-avatar { background: #6366f1; }
.msg.assistant .msg-avatar { background: #3b82f6; }
.msg-bubble {
    padding: 10px 14px; border-radius: 12px; font-size: 14px;
    line-height: 1.6; color: #333; word-wrap: break-word;
}
.msg.user .msg-bubble { background: #3b82f6; color: #fff; border-bottom-right-radius: 4px; }
.msg.assistant .msg-bubble { background: #f3f4f6; border-bottom-left-radius: 4px; }
.msg-time { font-size: 11px; color: #9ca3af; margin-top: 4px; text-align: right; }
.msg.user .msg-time { text-align: left; }

/* ===== 输入区 ===== */
.input-area {
    border-top: 1px solid #e5e7eb; padding: 12px 20px;
    display: flex; gap: 8px; align-items: flex-end;
}
.input-area .attach-btn {
    background: none; border: none; cursor: pointer; padding: 8px;
    border-radius: 6px; color: #6b7280; display: flex; align-items: center; justify-content: center;
}
.input-area .attach-btn:hover { background: #f3f4f6; color: #333; }
.input-area textarea {
    flex: 1; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px 14px;
    font-size: 14px; outline: none; resize: none; min-height: 20px; max-height: 120px;
    font-family: inherit; line-height: 1.5;
}
.input-area textarea:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59,130,246,0.1); }
.input-area .send-btn {
    background: #3b82f6 !important; color: #fff !important; border: none !important;
    border-radius: 8px !important; width: 36px !important; height: 36px !important;
    min-width: 36px !important; padding: 0 !important; cursor: pointer;
    display: flex !important; align-items: center !important; justify-content: center !important;
}
.input-area .send-btn:hover { background: #2563eb !important; }
.input-area .send-btn svg { width: 18px; height: 18px; fill: #fff; }

/* ===== Gradio 组件隐藏 ===== */
.gradio-row { gap: 0 !important; }
.block { border: none !important; box-shadow: none !important; }

/* ===== 会话下拉选择框样式覆盖 ===== */
.session-select { width: 100%; }
.session-select > label { display: none !important; }
.session-select .wrap { background: transparent !important; border: none !important; padding: 0 !important; box-shadow: none !important; }
.session-select .wrap .secondary-wrap { display: none !important; }
.session-select input, .session-select select {
    width: 100% !important; padding: 8px 12px !important;
    border: 1px solid #e5e7eb !important; border-radius: 6px !important;
    font-size: 13px !important; background: #fff !important;
    box-sizing: border-box !important;
}

/* 清空按钮样式 */
.clear-btn {
    background: #f3f4f6 !important; border: 1px solid #e5e7eb !important;
    color: #6b7280 !important; border-radius: 6px !important;
    font-size: 12px !important; padding: 4px 8px !important; cursor: pointer;
}
.clear-btn:hover { background: #e5e7eb !important; color: #333 !important; }

/* 滚动条美化 */
.session-list::-webkit-scrollbar,
.chat-messages::-webkit-scrollbar { width: 4px; }
.session-list::-webkit-scrollbar-track,
.chat-messages::-webkit-scrollbar-track { background: transparent; }
.session-list::-webkit-scrollbar-thumb,
.chat-messages::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 4px; }
.session-list::-webkit-scrollbar-thumb:hover,
.chat-messages::-webkit-scrollbar-thumb:hover { background: #9ca3af; }
"""

# ============================================================
# HTML 组件
# ============================================================
TOP_NAV_HTML = """
<div class="top-nav">
    <nav>
        <a class="active">探索</a>
        <a>工作室</a>
        <a>知识库</a>
        <a>工具市场</a>
    </nav>
</div>
"""

SIDEBAR_HTML = """
<div class="left-sidebar">
    <div style="margin-bottom:24px">
        <div class="sidebar-label">菜单</div>
    </div>
    <div class="menu-item">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <span>探索</span>
    </div>
    <div class="menu-item active">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
        <span>工作区</span>
    </div>
    <div style="padding-left:36px; margin-top:4px">
        <div class="menu-item active" style="font-size:13px">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            <span>网站小助手</span>
        </div>
    </div>
</div>
"""

CHAT_HEADER_HTML = """
<div class="chat-header">
    <div class="avatar">助</div>
    <div class="info">
        <div class="name">网站小助手</div>
        <div class="time">在线</div>
    </div>
</div>
"""


# ============================================================
# 核心函数
# ============================================================
def _now():
    from datetime import datetime
    return datetime.now().strftime("%H:%M")


def _make_greeting():
    return [{"role": "assistant", "content": "你好！我是你的AI助手，有什么可以帮助你的吗？"}]


def _make_first_session():
    """创建初始会话数据"""
    sid = "session_" + uuid.uuid4().hex[:8]
    ts = _now()
    return sid, {
        sid: {
            "title": "新会话",
            "time": ts,
            "messages": _make_greeting(),
        }
    }


FIRST_SID, FIRST_ALL = _make_first_session()


def chat_fn(user_msg, chatbot_history, session_id, all_sessions):
    if not user_msg or not user_msg.strip():
        yield chatbot_history, session_id, all_sessions
        return

    session_id = session_id or list(all_sessions.keys())[0]
    chatbot_history = list(chatbot_history or [])
    chatbot_history.append({"role": "user", "content": user_msg})

    # 显示用户消息
    yield chatbot_history, session_id, all_sessions

    # 更新会话标题（首条消息）
    if len(chatbot_history) == 1:
        all_sessions[session_id]["title"] = user_msg[:20]

    # 流式生成回复
    response = ""
    try:
        for chunk in agent.chat_stream(user_msg, session_id):
            response += chunk
            display = list(chatbot_history)
            display.append({"role": "assistant", "content": response})
            yield display, session_id, all_sessions
    except Exception as e:
        response = f"抱歉，处理您的问题时出现错误：{str(e)}"
        display = list(chatbot_history)
        display.append({"role": "assistant", "content": response})
        yield display, session_id, all_sessions

    # 保存到会话历史
    all_sessions[session_id]["messages"] = list(display)


def clear_fn():
    sid, all_s = _make_first_session()
    return _make_greeting(), sid, all_s, sid


def create_session(all_sessions):
    sid = "session_" + uuid.uuid4().hex[:8]
    ts = _now()
    all_sessions[sid] = {"title": "新会话", "time": ts, "messages": _make_greeting()}
    return all_sessions, sid, _make_greeting(), sid, sid


def switch_session(sel, all_sessions):
    if not sel or sel not in all_sessions:
        sel = list(all_sessions.keys())[0] if all_sessions else FIRST_SID
    return sel, all_sessions[sel]["messages"], sel


def search_sessions(query, all_sessions):
    q = query.strip().lower()
    if not q:
        return all_sessions, FIRST_SID, FIRST_ALL[FIRST_SID]["messages"], FIRST_SID
    for sid, info in all_sessions.items():
        if q in info["title"].lower():
            return all_sessions, sid, info["messages"], sid
    first = list(all_sessions.keys())[0]
    return all_sessions, first, all_sessions[first]["messages"], first


def build_demo():
    with gr.Blocks(title="校园答疑智能客服") as demo:
        # 顶部导航
        gr.HTML(TOP_NAV_HTML)

        # ---- State ----
        session_id_state = gr.State(value=FIRST_SID)
        all_sessions_state = gr.State(value=FIRST_ALL)

        with gr.Row(elem_classes="main-row", equal_height=True):
            # ===== 左侧栏 =====
            with gr.Column(scale=0, min_width=180, elem_classes="col-left"):
                gr.HTML(SIDEBAR_HTML)

            # ===== 会话列表 =====
            with gr.Column(scale=0, min_width=260, elem_classes="col-sessions"):
                gr.HTML("""
                    <div class="session-header">
                        <h3>会话列表</h3>
                        <div class="session-header-btns">
                            <button title="新建会话" id="btn-new-sess">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                            </button>
                        </div>
                    </div>
                """)

                with gr.Row(elem_classes="session-search"):
                    search_box = gr.Textbox(
                        placeholder="搜索会话...",
                        show_label=False,
                        lines=1,
                        container=False
                    )

                session_dropdown = gr.Dropdown(
                    choices=[(f"{FIRST_ALL[FIRST_SID]['title']}  {FIRST_ALL[FIRST_SID]['time']}", FIRST_SID)],
                    value=FIRST_SID,
                    show_label=False,
                    interactive=True,
                    elem_classes="session-select"
                )

                new_btn = gr.Button("新建会话", visible=False)
                switch_btn = gr.Button("切换", visible=False)
                hidden_sel = gr.Textbox(visible=False)

            # ===== 聊天区 =====
            with gr.Column(scale=3, min_width=400, elem_classes="col-chat"):
                gr.HTML(CHAT_HEADER_HTML)

                chatbot = gr.Chatbot(
                    value=_make_greeting(),
                    height=520,
                    show_label=False,
                )

                with gr.Row(elem_classes="input-area"):
                    attach = gr.Button("", elem_classes="attach-btn", min_width=36)
                    msg_input = gr.Textbox(
                        placeholder="输入消息...(Shift+Enter换行, Enter发送)",
                        show_label=False,
                        lines=1,
                        max_lines=6,
                        scale=5,
                        container=False
                    )
                    send_btn = gr.Button("发送", elem_classes="send-btn", min_width=36)

        # ============================================================
        # 事件绑定
        # ============================================================
        chat_outputs = [chatbot, session_id_state, all_sessions_state]

        msg_input.submit(
            chat_fn,
            inputs=[msg_input, chatbot, session_id_state, all_sessions_state],
            outputs=chat_outputs,
        ).then(lambda: "", outputs=msg_input)

        send_btn.click(
            chat_fn,
            inputs=[msg_input, chatbot, session_id_state, all_sessions_state],
            outputs=chat_outputs,
        ).then(lambda: "", outputs=msg_input)

        # 新建会话
        new_btn.click(
            create_session,
            inputs=[all_sessions_state],
            outputs=[all_sessions_state, session_id_state, chatbot, session_dropdown, hidden_sel],
        )

        # 切换会话
        switch_btn.click(
            switch_session,
            inputs=[hidden_sel, all_sessions_state],
            outputs=[session_id_state, chatbot, session_dropdown],
        )

        # 下拉切换
        session_dropdown.select(
            switch_session,
            inputs=[session_dropdown, all_sessions_state],
            outputs=[session_id_state, chatbot, session_dropdown],
        )

        # 搜索
        search_box.change(
            search_sessions,
            inputs=[search_box, all_sessions_state],
            outputs=[all_sessions_state, session_id_state, chatbot, session_dropdown],
        )

    return demo


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    demo = build_demo()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        css=CUSTOM_CSS,
        theme=gr.themes.Soft(),
    )
