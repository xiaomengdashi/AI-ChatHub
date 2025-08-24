import requests
from typing import Union, Iterator, Any
from .base_client import BaseAIClient

class AnthropicClient(BaseAIClient):
    """Anthropic AI客户端"""
    
    def __init__(self, api_key: str, base_url: str = None):
        # 如果没有提供base_url，使用默认的Anthropic API地址
        if not base_url:
            base_url = "https://api.anthropic.com"
        super().__init__(api_key, base_url)
    
    @property
    def provider_name(self) -> str:
        return 'anthropic'
    
    def call_sync(self, model: str, message: str, **kwargs) -> str:
        """
        同步调用Anthropic API
        
        Args:
            model: 模型名称
            message: 用户消息
            **kwargs: 其他参数
            
        Returns:
            AI响应内容
        """
        params = self._get_default_params()
        params.update(kwargs)
        
        url = f"{self.base_url}/v1/messages"
        
        # 构建消息列表
        messages = []
        
        # Anthropic API的系统消息是单独的参数
        system_message = kwargs.get('system_message', '')
        
        messages.append({
            "role": "user",
            "content": message
        })
        
        payload = {
            "model": model,
            "max_tokens": params.get('max_tokens', 2048),
            "messages": messages,
            "temperature": params.get('temperature', 0.7),
            "top_p": params.get('top_p', 1.0)
        }
        
        # 如果有系统消息，添加到payload中
        if system_message:
            payload["system"] = system_message
        
        # 添加stop参数支持（Anthropic使用stop_sequences）
        if 'stop' in kwargs and kwargs['stop']:
            payload['stop_sequences'] = kwargs['stop'] if isinstance(kwargs['stop'], list) else [kwargs['stop']]
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                headers=headers, 
                timeout=params.get('timeout', 60)
            )
            response.raise_for_status()
            
            result = response.json()
            if 'content' in result and len(result['content']) > 0:
                return result['content'][0]['text']
            else:
                return "抱歉，模型没有返回有效响应。"
                
        except requests.exceptions.RequestException as e:
            return self._handle_error(e, "Anthropic API调用")
        except Exception as e:
            return self._handle_error(e, "Anthropic API调用")
    
    def call_stream(self, model: str, message: str, **kwargs) -> Union[Iterator[Any], None]:
        """
        流式调用Anthropic API
        
        Args:
            model: 模型名称
            message: 用户消息
            **kwargs: 其他参数
            
        Returns:
            流式响应迭代器或None
        """
        params = self._get_default_params()
        params.update(kwargs)
        
        url = f"{self.base_url}/v1/messages"
        
        # 构建消息列表
        messages = []
        
        # Anthropic API的系统消息是单独的参数
        system_message = kwargs.get('system_message', '')
        
        messages.append({
            "role": "user",
            "content": message
        })
        
        payload = {
            "model": model,
            "max_tokens": params.get('max_tokens', 2048),
            "messages": messages,
            "temperature": params.get('temperature', 0.7),
            "top_p": params.get('top_p', 1.0),
            "stream": True
        }
        
        # 如果有系统消息，添加到payload中
        if system_message:
            payload["system"] = system_message
        
        # 添加stop参数支持（Anthropic使用stop_sequences）
        if 'stop' in kwargs and kwargs['stop']:
            payload['stop_sequences'] = kwargs['stop'] if isinstance(kwargs['stop'], list) else [kwargs['stop']]
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                headers=headers, 
                stream=True,
                timeout=params.get('timeout', 60)
            )
            response.raise_for_status()
            
            def stream_generator():
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]
                            if data.strip() == '[DONE]':
                                break
                            try:
                                import json
                                chunk = json.loads(data)
                                if chunk.get('type') == 'content_block_delta':
                                    delta = chunk.get('delta', {})
                                    if 'text' in delta:
                                        yield delta['text']
                            except json.JSONDecodeError:
                                continue
            
            return stream_generator()
            
        except requests.exceptions.RequestException as e:
            print(f"Anthropic流式API调用错误: {e}")
            return None
        except Exception as e:
            print(f"Anthropic流式API调用异常: {e}")
            return None
    
    def _get_default_params(self) -> dict:
        """获取默认参数"""
        return {
            'max_tokens': 2048,
            'temperature': 0.7,
            'top_p': 1.0,
            'timeout': 60
        }