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

class DeepSeekClient(BaseAIClient):
    """DeepSeek AI客户端"""
    
    def __init__(self, api_key: str, base_url: str = None):
        if not base_url:
            raise ValueError("base_url is required for DeepSeekClient")
        super().__init__(api_key, base_url)
    
    @property
    def provider_name(self) -> str:
        return 'deepseek'
    
    def call_sync(self, model: str, message: str, **kwargs) -> str:
        """
        同步调用DeepSeek API
        
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
            "max_tokens": params.get('max_tokens', 2048),
            "temperature": params.get('temperature', 0.7)
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
            return self._handle_error(e, "DeepSeek API调用")
        except Exception as e:
            return self._handle_error(e, "处理DeepSeek响应")
    
    def call_stream(self, model: str, message: str, **kwargs) -> Union[Iterator[MockStreamChunk], None]:
        """
        流式调用DeepSeek API
        
        Args:
            model: 模型名称
            message: 用户消息
            **kwargs: 其他参数
            
        Returns:
            流式响应迭代器或None
        """
        params = self._get_default_params()
        params.update(kwargs)
        
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "stream": True,
            "max_tokens": params.get('max_tokens', 2048),
            "temperature": params.get('temperature', 0.7)
        }
        
        try:
            response = requests.post(
                url, 
                headers=headers, 
                json=payload, 
                stream=True,
                timeout=params.get('timeout', 30)
            )
            response.raise_for_status()
            
            return self._parse_stream_response(response)
            
        except Exception as e:
            return None
    
    def _parse_stream_response(self, response) -> Iterator[MockStreamChunk]:
        """
        解析DeepSeek的SSE流式响应
        
        Args:
            response: requests响应对象
            
        Yields:
            模拟OpenAI格式的流式响应块
        """
        for chunk in response.iter_content(chunk_size=None):
            if chunk:
                try:
                    chunk_text = chunk.decode('utf-8')
                    lines = chunk_text.split("\n")
                    for line in lines:
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                return
                            data = json.loads(data_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                content = data["choices"][0].get("delta", {}).get("content", "")
                                if content:
                                    yield MockStreamChunk(content=content)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue