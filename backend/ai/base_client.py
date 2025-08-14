from abc import ABC, abstractmethod
from typing import Union, Iterator, Any

class BaseAIClient(ABC):
    """AI客户端抽象基类"""
    
    def __init__(self, api_key: str, base_url: str = None):
        """
        初始化AI客户端
        
        Args:
            api_key: API密钥
            base_url: 基础URL（可选）
        """
        self.api_key = api_key
        self.base_url = base_url
    
    @abstractmethod
    def call_sync(self, model: str, message: str, **kwargs) -> str:
        """
        同步调用AI API
        
        Args:
            model: 模型名称
            message: 用户消息
            **kwargs: 其他参数
            
        Returns:
            AI响应内容
        """
        pass
    
    @abstractmethod
    def call_stream(self, model: str, message: str, **kwargs) -> Union[Iterator[Any], None]:
        """
        流式调用AI API
        
        Args:
            model: 模型名称
            message: 用户消息
            **kwargs: 其他参数
            
        Returns:
            流式响应迭代器或None
        """
        pass
    
    def call_api(self, model: str, message: str, stream: bool = False, **kwargs) -> Union[str, Iterator[Any], None]:
        """
        统一的API调用接口
        
        Args:
            model: 模型名称
            message: 用户消息
            stream: 是否使用流式输出
            **kwargs: 其他参数
            
        Returns:
            同步调用返回字符串，流式调用返回迭代器
        """
        if stream:
            return self.call_stream(model, message, **kwargs)
        else:
            return self.call_sync(model, message, **kwargs)
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        提供商名称
        
        Returns:
            提供商标识符
        """
        pass
    
    def _get_default_params(self) -> dict:
        """
        获取默认参数
        
        Returns:
            默认参数字典
        """
        return {
            'temperature': 0.7,
            'max_tokens': 2048,
            'timeout': 30
        }
    
    def _handle_error(self, error: Exception, context: str = '') -> str:
        """
        统一的错误处理
        
        Args:
            error: 异常对象
            context: 错误上下文
            
        Returns:
            错误消息
        """
        error_msg = f"{context}失败: {str(error)}" if context else f"API调用失败: {str(error)}"
        return error_msg