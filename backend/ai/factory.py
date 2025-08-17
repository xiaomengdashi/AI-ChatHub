from typing import Dict, Type, Optional
from .base_client import BaseAIClient
from .openai_client import OpenAIClient
from .siliconflow_client import SiliconFlowClient
from .baidu_client import BaiduClient
from .alibaba_client import AlibabaClient
from .zhipu_client import ZhipuClient
from .deepseek_client import DeepSeekClient

class AIClientFactory:
    """AI客户端工厂类"""
    
    # 注册的客户端类映射
    _clients: Dict[str, Type[BaseAIClient]] = {
        'openai': OpenAIClient,
        'siliconflow': SiliconFlowClient,
        'baidu': BaiduClient,
        'alibaba': AlibabaClient,
        'zhipu': ZhipuClient,
        'deepseek': DeepSeekClient
    }
    
    @classmethod
    def create_client(cls, provider: str, api_key: str, base_url: str = None) -> BaseAIClient:
        """
        根据提供商创建对应的AI客户端
        
        Args:
            provider: 提供商名称
            api_key: API密钥
            base_url: 可选的基础URL，如果不提供则从数据库获取
            
        Returns:
            对应的AI客户端实例
            
        Raises:
            ValueError: 当提供商不支持时
        """
        if provider not in cls._clients:
            raise ValueError(f"不支持的AI提供商: {provider}。支持的提供商: {list(cls._clients.keys())}")
        
        # 如果没有提供base_url，尝试从数据库获取
        if base_url is None:
            base_url = cls._get_base_url_from_db(provider, api_key)
        
        client_class = cls._clients[provider]
        return client_class(api_key, base_url)
    
    @classmethod
    def get_supported_providers(cls) -> list:
        """
        获取支持的提供商列表
        
        Returns:
            支持的提供商名称列表
        """
        return list(cls._clients.keys())
    
    @classmethod
    def _get_base_url_from_db(cls, provider: str, api_key: str) -> str:
        """
        从数据库获取base_url
        
        Args:
            provider: 提供商名称
            api_key: API密钥
            
        Returns:
            base_url（如果数据库查询失败，返回默认URL）
        """
        # 默认URL映射（作为fallback）
        default_urls = {
            'siliconflow': 'https://api.siliconflow.cn/v1',
            'baidu': 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat',
            'alibaba': 'https://dashscope.aliyuncs.com/api/v1',
            'zhipu': 'https://open.bigmodel.cn/api/paas/v4',
            'deepseek': 'https://api.deepseek.com'
        }
        
        try:
            # 导入数据库模型（延迟导入避免循环依赖）
            from models.models import ApiKey, Provider
            
            # 首先尝试从ApiKey表获取自定义的base_url
            api_key_record = ApiKey.query.filter_by(
                model_provider=provider, 
                api_key=api_key, 
                is_active=True
            ).first()
            
            if api_key_record and api_key_record.base_url:
                return api_key_record.base_url
            
            # 如果没有自定义base_url，从Provider表获取默认base_url
            provider_record = Provider.query.filter_by(
                provider_key=provider, 
                is_active=True
            ).first()
            
            if provider_record and provider_record.default_base_url:
                return provider_record.default_base_url
                
        except Exception as e:
            # 如果数据库查询失败，使用默认URL
            print(f"从数据库获取base_url失败，使用默认URL: {e}")
            
        # 返回默认URL作为fallback
        return default_urls.get(provider, '')
    
    @classmethod
    def register_client(cls, provider: str, client_class: Type[BaseAIClient]):
        """
        注册新的AI客户端类
        
        Args:
            provider: 提供商名称
            client_class: 客户端类
        """
        cls._clients[provider] = client_class