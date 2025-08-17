import requests
from openai import OpenAI
from typing import Union, Iterator, Any
from .base_client import BaseAIClient

class OpenAIClient(BaseAIClient):
    """OpenAI官方API客户端"""
    
    def __init__(self, api_key: str, base_url: str = None):
        # 如果没有提供base_url，使用默认的OpenAI API地址
        if not base_url:
            base_url = "https://api.openai.com/v1"
        super().__init__(api_key, base_url)
    
    @property
    def provider_name(self) -> str:
        return 'openai'
    
    def call_sync(self, model: str, message: str, **kwargs) -> str:
        """
        同步调用OpenAI API
        
        Args:
            model: 模型名称 (如: gpt-3.5-turbo, gpt-4, gpt-4o等)
            message: 用户消息
            **kwargs: 其他参数
            
        Returns:
            AI响应内容
        """
        params = self._get_default_params()
        params.update(kwargs)
        
        url = f"{self.base_url}/chat/completions"
        
        # 构建消息列表，支持系统消息
        messages = []
        if 'system_message' in kwargs:
            messages.append({
                "role": "system",
                "content": kwargs['system_message']
            })
        
        messages.append({
            "role": "user",
            "content": message
        })
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": params.get('max_tokens', 2048),
            "temperature": params.get('temperature', 0.7),
            "top_p": params.get('top_p', 1.0),
            "frequency_penalty": params.get('frequency_penalty', 0.0),
            "presence_penalty": params.get('presence_penalty', 0.0)
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
                timeout=params.get('timeout', 60)  # OpenAI API可能需要更长时间
            )
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                return "抱歉，模型没有返回有效响应。"
                
        except requests.exceptions.RequestException as e:
            return self._handle_error(e, "OpenAI API调用")
        except Exception as e:
            return self._handle_error(e, "处理OpenAI响应")
    
    def call_stream(self, model: str, message: str, **kwargs) -> Union[Iterator[Any], None]:
        """
        流式调用OpenAI API
        
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
            
            # 构建消息列表，支持系统消息
            messages = []
            if 'system_message' in kwargs:
                messages.append({
                    "role": "system",
                    "content": kwargs['system_message']
                })
            
            messages.append({
                "role": "user",
                "content": message
            })
            
            return client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                max_tokens=params.get('max_tokens', 2048),
                temperature=params.get('temperature', 0.7),
                top_p=params.get('top_p', 1.0),
                frequency_penalty=params.get('frequency_penalty', 0.0),
                presence_penalty=params.get('presence_penalty', 0.0)
            )
            
        except Exception as e:
            self._handle_error(e, "OpenAI流式API调用")
            return None
    
    def _get_default_params(self) -> dict:
        """
        获取默认参数，针对OpenAI API优化
        
        Returns:
            默认参数字典
        """
        return {
            'max_tokens': 2048,
            'temperature': 0.7,
            'top_p': 1.0,
            'frequency_penalty': 0.0,
            'presence_penalty': 0.0,
            'timeout': 60  # OpenAI API通常需要更长的超时时间
        }