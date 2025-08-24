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

class BaiduClient(BaseAIClient):
    """百度文心一言AI客户端"""
    
    def __init__(self, api_key: str, base_url: str = None):
        if not base_url:
            raise ValueError("base_url is required for BaiduClient")
        super().__init__(api_key, base_url)
        # 百度API的模型端点映射
        self.model_endpoints = {
            'ernie-bot': 'completions',
            'ernie-bot-turbo': 'eb-instant',
            'ernie-bot-4': 'completions_pro',
            'ernie-3.5-8k': 'completions',
            'ernie-3.5-8k-0205': 'ernie_bot_8k'
        }
    
    @property
    def provider_name(self) -> str:
        return 'baidu'
    
    def _get_endpoint_url(self, model: str) -> str:
        """
        根据模型获取对应的端点URL
        
        Args:
            model: 模型名称
            
        Returns:
            完整的API端点URL
        """
        endpoint = self.model_endpoints.get(model, 'completions')
        return f"{self.base_url}/{endpoint}?access_token={self.api_key}"
    
    def call_sync(self, model: str, message: str, **kwargs) -> str:
        """
        同步调用百度文心一言API
        
        Args:
            model: 模型名称
            message: 用户消息
            **kwargs: 其他参数
            
        Returns:
            AI响应内容
        """
        params = self._get_default_params()
        params.update(kwargs)
        
        url = self._get_endpoint_url(model)
        
        payload = {
            "messages": [{"role": "user", "content": message}],
            "temperature": params.get('temperature', 0.7),
            "max_output_tokens": params.get('max_tokens', 2048)
        }
        
        # 添加stop参数支持
        if 'stop' in kwargs and kwargs['stop']:
            payload['stop'] = kwargs['stop']
        
        headers = {
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
            if 'result' in result:
                return result['result']
            else:
                return "抱歉，模型没有返回有效响应。"
                
        except requests.exceptions.RequestException as e:
            return self._handle_error(e, "百度文心一言API调用")
        except Exception as e:
            return self._handle_error(e, "处理百度文心一言响应")
    
    def call_stream(self, model: str, message: str, **kwargs) -> Union[Iterator[MockStreamChunk], None]:
        """
        流式调用百度文心一言API
        
        Args:
            model: 模型名称
            message: 用户消息
            **kwargs: 其他参数
            
        Returns:
            流式响应迭代器或None
        """
        params = self._get_default_params()
        params.update(kwargs)
        
        url = self._get_endpoint_url(model)
        
        payload = {
            "messages": [{"role": "user", "content": message}],
            "temperature": params.get('temperature', 0.7),
            "max_output_tokens": params.get('max_tokens', 2048),
            "stream": True
        }
        
        # 添加stop参数支持
        if 'stop' in kwargs and kwargs['stop']:
            payload['stop'] = kwargs['stop']
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                url, 
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
        解析百度文心一言的SSE流式响应
        
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
                    if 'result' in data:
                        content = data['result']
                        if content:
                            yield MockStreamChunk(content=content)
                except (json.JSONDecodeError, KeyError):
                    continue