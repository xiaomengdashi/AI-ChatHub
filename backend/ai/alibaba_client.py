import requests
import json
from typing import Union, Iterator, Any
from .base_client import BaseAIClient

class MockChoice:
    """模拟OpenAI的Choice对象"""
    def __init__(self, content=None, reasoning_content=None):
        self.delta = MockDelta(content, reasoning_content)

class MockDelta:
    """模拟OpenAI的Delta对象"""
    def __init__(self, content=None, reasoning_content=None):
        self.content = content
        self.reasoning_content = reasoning_content

class MockStreamChunk:
    """模拟OpenAI的流式响应块"""
    def __init__(self, content=None, reasoning_content=None):
        self.choices = [MockChoice(content, reasoning_content)]

class AlibabaClient(BaseAIClient):
    """阿里云百炼AI客户端"""
    
    def __init__(self, api_key: str, base_url: str = None):
        if not base_url:
            raise ValueError("base_url is required for AlibabaClient")
        super().__init__(api_key, base_url)
    
    @property
    def provider_name(self) -> str:
        return 'alibaba'
    
    def call_sync(self, model: str, message: str, **kwargs) -> str:
        """
        同步调用阿里云百炼API
        
        Args:
            model: 模型名称
            message: 用户消息
            **kwargs: 其他参数
            
        Returns:
            AI响应内容
        """
        params = self._get_default_params()
        params.update(kwargs)
        
        payload = {
            "model": model,
            "input": {
                "messages": [{"role": "user", "content": message}]
            },
            "parameters": {
                "temperature": params.get('temperature', 0.7),
                "max_tokens": params.get('max_tokens', 2048)
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                self.base_url, 
                json=payload, 
                headers=headers, 
                timeout=params.get('timeout', 30)
            )
            response.raise_for_status()
            
            result = response.json()
            if 'output' in result and 'text' in result['output']:
                return result['output']['text']
            else:
                return "抱歉，模型没有返回有效响应。"
                
        except requests.exceptions.RequestException as e:
            return self._handle_error(e, "阿里云百炼API调用")
        except Exception as e:
            return self._handle_error(e, "处理阿里云百炼响应")
    
    def call_stream(self, model: str, message: str, **kwargs) -> Union[Iterator[MockStreamChunk], None]:
        """
        流式调用阿里云百炼API
        
        Args:
            model: 模型名称
            message: 用户消息
            **kwargs: 其他参数
            
        Returns:
            流式响应迭代器或None
        """
        params = self._get_default_params()
        params.update(kwargs)
        
        payload = {
            "model": model,
            "input": {
                "messages": [{"role": "user", "content": message}]
            },
            "parameters": {
                "temperature": params.get('temperature', 0.7),
                "max_tokens": params.get('max_tokens', 2048),
                "incremental_output": True
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-SSE": "enable"
        }
        
        try:
            response = requests.post(
                self.base_url, 
                json=payload, 
                headers=headers, 
                stream=True, 
                timeout=params.get('timeout', 30)
            )
            response.raise_for_status()
            return self._parse_stream_response(response)
        except Exception as e:
            return None
    
    def _parse_stream_response(self, response) -> Iterator[MockStreamChunk]:
        """
        解析阿里云百炼的SSE流式响应
        
        Args:
            response: requests响应对象
            
        Yields:
            模拟OpenAI格式的流式响应块
        """
        for line in response.iter_lines(decode_unicode=True):
            if line and line.startswith('data:'):
                try:
                    data_str = line[5:].strip()
                    if data_str == '[DONE]':
                        return
                    data = json.loads(data_str)
                    if 'output' in data and 'text' in data['output']:
                        content = data['output']['text']
                        if content:
                            yield MockStreamChunk(content=content)
                except (json.JSONDecodeError, KeyError):
                    continue