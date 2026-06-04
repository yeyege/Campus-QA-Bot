# -*- coding: utf-8 -*-
"""
校园答疑智能客服 - 前端启动脚本
"""
import os
import sys

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import build_demo

print("正在初始化...")
demo = build_demo()
print("启动前端服务: http://127.0.0.1:7860")

demo.launch(
    server_name="127.0.0.1",
    server_port=7860,
    share=False,
    show_error=True
)
