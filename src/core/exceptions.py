"""
自定义异常类 - 统一错误处理
"""


class CampusQAError(Exception):
    """基础异常类"""
    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code
        super().__init__(self.message)


class LLMError(CampusQAError):
    """LLM调用错误"""
    def __init__(self, message: str = "LLM服务调用失败"):
        super().__init__(message, code=503)


class RetrievalError(CampusQAError):
    """检索错误"""
    def __init__(self, message: str = "知识库检索失败"):
        super().__init__(message, code=500)


class SessionError(CampusQAError):
    """会话错误"""
    def __init__(self, message: str = "会话处理失败"):
        super().__init__(message, code=400)


class ConfigError(CampusQAError):
    """配置错误"""
    def __init__(self, message: str = "配置文件错误"):
        super().__init__(message, code=500)
