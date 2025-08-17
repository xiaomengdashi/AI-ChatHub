from .base_client import BaseAIClient
from .openai_client import OpenAIClient
from .siliconflow_client import SiliconFlowClient
from .baidu_client import BaiduClient
from .alibaba_client import AlibabaClient
from .zhipu_client import ZhipuClient
from .factory import AIClientFactory

# 为了保持向后兼容，提供统一的AIClient类
class AIClient:
    """统一的AI客户端接口，保持向后兼容"""
    
    @staticmethod
    def call_ai_api(provider: str, model: str, message: str, api_key_or_record, stream: bool = False, **kwargs):
        """
        统一的AI API调用接口
        
        Args:
            provider: 提供商名称
            model: 模型名称
            message: 用户消息
            api_key_or_record: API密钥字符串或ApiKey对象
            stream: 是否流式调用
            **kwargs: 其他参数
            
        Returns:
            AI响应内容或流式响应迭代器
        """
        try:
            # 处理api_key_or_record参数
            if hasattr(api_key_or_record, 'api_key'):
                # 如果是ApiKey对象
                api_key = api_key_or_record.api_key
                base_url = api_key_or_record.base_url
            else:
                # 如果是字符串
                api_key = api_key_or_record
                base_url = None
            
            client = AIClientFactory.create_client(provider, api_key, base_url)
            return client.call_api(model, message, stream=stream, **kwargs)
        except Exception as e:
            if stream:
                return None
            else:
                return f"抱歉，调用{provider} AI API时发生错误: {str(e)}"
    
    # 保持向后兼容的方法
    @staticmethod
    def call_siliconflow_api(model: str, message: str, api_key: str, **kwargs):
        """调用硅基流动API（向后兼容）"""
        return AIClient.call_ai_api('siliconflow', model, message, api_key, stream=False, **kwargs)
    
    @staticmethod
    def call_siliconflow_api_sync(model: str, message: str, api_key: str, **kwargs):
        """同步调用硅基流动API（向后兼容）"""
        return AIClient.call_ai_api('siliconflow', model, message, api_key, stream=False, **kwargs)
    
    @staticmethod
    def call_siliconflow_api_stream(model: str, message: str, api_key: str, **kwargs):
        """流式调用硅基流动API（向后兼容）"""
        return AIClient.call_ai_api('siliconflow', model, message, api_key, stream=True, **kwargs)

__all__ = [
    'BaseAIClient',
    'OpenAIClient',
    'SiliconFlowClient',
    'BaiduClient',
    'AlibabaClient',
    'ZhipuClient',
    'AIClientFactory',
    'AIClient'
]