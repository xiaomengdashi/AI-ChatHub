import requests
from openai import OpenAI
from typing import Union, Iterator, Any
from .base_client import BaseAIClient

class ZhipuClient(BaseAIClient):
    """智谱AI客户端"""
    
    def __init__(self, api_key: str, base_url: str = None):
        if not base_url:
            raise ValueError("base_url is required for ZhipuClient")
        super().__init__(api_key, base_url)
    
    @property
    def provider_name(self) -> str:
        return 'zhipu'
    
    def call_sync(self, model: str, message: str, **kwargs) -> str:
        """
        同步调用智谱AI API
        
        Args:
            model: 模型名称
            message: 用户消息
            **kwargs: 其他参数
            
        Returns:
            AI响应内容
        """
        params = self._get_default_params()
        params.update(kwargs)
        
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "temperature": params.get('temperature', 0.7),
            "max_tokens": params.get('max_tokens', 2048)
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                headers=headers, 
                timeout=params.get('timeout', 30)
            )
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                return "抱歉，模型没有返回有效响应。"
                
        except requests.exceptions.RequestException as e:
            return self._handle_error(e, "智谱AI API调用")
        except Exception as e:
            return self._handle_error(e, "处理智谱AI响应")
    
    def call_stream(self, model: str, message: str, **kwargs) -> Union[Iterator[Any], None]:
        """
        流式调用智谱AI API
        
        Args:
            model: 模型名称
            message: 用户消息
            **kwargs: 其他参数
            
        Returns:
            流式响应迭代器或None
        """
        params = self._get_default_params()
        params.update(kwargs)
        
        try:
            client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
            
            return client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": message}],
                stream=True,
                max_tokens=params.get('max_tokens', 2048),
                temperature=params.get('temperature', 0.7)
            )
            
        except Exception as e:
            return None