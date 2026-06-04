"""
日志系统模块 - 结构化日志记录
"""
import os
import logging
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler


class Logger:
    """结构化日志记录器"""

    def __init__(self, name: str = "campus_qa", log_dir: str = "logs"):
        self.name = name
        self.log_dir = log_dir

        os.makedirs(log_dir, exist_ok=True)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """配置日志处理器"""
        # 控制台输出
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_format)

        # 文件输出（按大小轮转，最大10MB，保留5个备份）
        log_file = os.path.join(self.log_dir, "app.log")
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
        )
        file_handler.setFormatter(file_format)

        # 错误日志单独文件
        error_file = os.path.join(self.log_dir, "error.log")
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)

    def log_request(self, question: str, response: str, latency: float, session_id: str):
        """记录请求日志"""
        self.logger.info({
            "event": "chat_request",
            "question": question[:100],
            "response_length": len(response),
            "latency_ms": round(latency * 1000, 2),
            "session_id": session_id
        })

    def log_error(self, error: Exception, context: Optional[dict] = None):
        """记录错误日志"""
        self.logger.error({
            "event": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }, exc_info=True)

    def log_retrieval(self, question: str, results_count: int, best_score: float):
        """记录检索日志"""
        self.logger.debug({
            "event": "retrieval",
            "question": question[:50],
            "results_count": results_count,
            "best_score": round(best_score, 4)
        })

    def info(self, message: str, **kwargs):
        """记录信息日志"""
        self.logger.info({"message": message, **kwargs})

    def warning(self, message: str, **kwargs):
        """记录警告日志"""
        self.logger.warning({"message": message, **kwargs})

    def error(self, message: str, **kwargs):
        """记录错误日志"""
        self.logger.error({"message": message, **kwargs})

    def debug(self, message: str, **kwargs):
        """记录调试日志"""
        self.logger.debug({"message": message, **kwargs})


# 全局实例
logger = Logger()
