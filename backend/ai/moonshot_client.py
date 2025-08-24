import requests
from typing import Union, Iterator, Any
from .base_client import BaseAIClient

class MoonshotClient(BaseAIClient):
    """Moonshot AI客户端"""
    
    def __init__(self, api_key: str, base_url: str = None):
        # 如果没有提供base_url，使用默认的Moonshot API地址
        if not base_url:
            base_url = "https://api.moonshot.cn/v1"
        super().__init__(api_key, base_url)
    
    @property
    def provider_name(self) -> str:
        return 'moonshot'
    
    def call_sync(self, model: str, message: str, **kwargs) -> str:
        """
        同步调用Moonshot API
        
        Args:
            model: 模型名称 (如: moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k)
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
        
        # 添加stop参数支持
        if 'stop' in kwargs and kwargs['stop']:
            payload['stop'] = kwargs['stop']
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
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
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                return "抱歉，模型没有返回有效响应。"
                
        except requests.exceptions.RequestException as e:
            return self._handle_error(e, "Moonshot API调用")
        except Exception as e:
            return self._handle_error(e, "Moonshot API调用")
    
    def call_stream(self, model: str, message: str, **kwargs) -> Union[Iterator[Any], None]:
        """
        流式调用Moonshot API
        
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
            "presence_penalty": params.get('presence_penalty', 0.0),
            "stream": True
        }
        
        # 添加stop参数支持
        if 'stop' in kwargs and kwargs['stop']:
            payload['stop'] = kwargs['stop']
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
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
                                if 'choices' in chunk and len(chunk['choices']) > 0:
                                    delta = chunk['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield delta['content']
                            except json.JSONDecodeError:
                                continue
            
            return stream_generator()
            
        except requests.exceptions.RequestException as e:
            print(f"Moonshot流式API调用错误: {e}")
            return None
        except Exception as e:
            print(f"Moonshot流式API调用异常: {e}")
            return None
    
    def _get_default_params(self) -> dict:
        """获取默认参数"""
        return {
            'max_tokens': 2048,
            'temperature': 0.7,
            'top_p': 1.0,
            'frequency_penalty': 0.0,
            'presence_penalty': 0.0,
            'timeout': 60
        }