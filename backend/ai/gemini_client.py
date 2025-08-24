import requests
from typing import Union, Iterator, Any
from .base_client import BaseAIClient

class GeminiClient(BaseAIClient):
    """Google Gemini AI客户端"""
    
    def __init__(self, api_key: str, base_url: str = None):
        # 如果没有提供base_url，使用默认的Gemini API地址
        if not base_url:
            base_url = "https://generativelanguage.googleapis.com"
        super().__init__(api_key, base_url)
    
    @property
    def provider_name(self) -> str:
        return 'gemini'
    
    def call_sync(self, model: str, message: str, **kwargs) -> str:
        """
        同步调用Gemini API
        
        Args:
            model: 模型名称
            message: 用户消息
            **kwargs: 其他参数
            
        Returns:
            AI响应内容
        """
        params = self._get_default_params()
        params.update(kwargs)
        
        # Gemini API使用不同的URL格式
        url = f"{self.base_url}/v1beta/models/{model}:generateContent"
        
        # 构建内容列表
        contents = []
        
        # 如果有系统消息，作为第一个用户消息发送
        system_message = kwargs.get('system_message', '')
        if system_message:
            contents.append({
                "parts": [{"text": f"System: {system_message}"}]
            })
        
        contents.append({
            "parts": [{"text": message}]
        })
        
        generation_config = {
            "temperature": params.get('temperature', 0.7),
            "topP": params.get('top_p', 1.0),
            "maxOutputTokens": params.get('max_tokens', 2048)
        }
        
        # 添加stop参数支持
        if 'stop' in kwargs and kwargs['stop']:
            generation_config['stopSequences'] = kwargs['stop'] if isinstance(kwargs['stop'], list) else [kwargs['stop']]
        
        payload = {
            "contents": contents,
            "generationConfig": generation_config
        }
        
        # Gemini API使用查询参数传递API密钥
        params_dict = {"key": self.api_key}
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                headers=headers,
                params=params_dict,
                timeout=params.get('timeout', 60)
            )
            response.raise_for_status()
            
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    if len(parts) > 0 and 'text' in parts[0]:
                        return parts[0]['text']
            
            return "抱歉，模型没有返回有效响应。"
                
        except requests.exceptions.RequestException as e:
            return self._handle_error(e, "Gemini API调用")
        except Exception as e:
            return self._handle_error(e, "Gemini API调用")
    
    def call_stream(self, model: str, message: str, **kwargs) -> Union[Iterator[Any], None]:
        """
        流式调用Gemini API
        
        Args:
            model: 模型名称
            message: 用户消息
            **kwargs: 其他参数
            
        Returns:
            流式响应迭代器或None
        """
        params = self._get_default_params()
        params.update(kwargs)
        
        # Gemini API使用不同的URL格式进行流式调用
        url = f"{self.base_url}/v1beta/models/{model}:streamGenerateContent"
        
        # 构建内容列表
        contents = []
        
        # 如果有系统消息，作为第一个用户消息发送
        system_message = kwargs.get('system_message', '')
        if system_message:
            contents.append({
                "parts": [{"text": f"System: {system_message}"}]
            })
        
        contents.append({
            "parts": [{"text": message}]
        })
        
        generation_config = {
            "temperature": params.get('temperature', 0.7),
            "topP": params.get('top_p', 1.0),
            "maxOutputTokens": params.get('max_tokens', 2048)
        }
        
        # 添加stop参数支持
        if 'stop' in kwargs and kwargs['stop']:
            generation_config['stopSequences'] = kwargs['stop'] if isinstance(kwargs['stop'], list) else [kwargs['stop']]
        
        payload = {
            "contents": contents,
            "generationConfig": generation_config
        }
        
        # Gemini API使用查询参数传递API密钥
        params_dict = {"key": self.api_key}
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                headers=headers,
                params=params_dict,
                stream=True,
                timeout=params.get('timeout', 60)
            )
            response.raise_for_status()
            
            def stream_generator():
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        # Gemini流式响应可能不使用标准的SSE格式
                        try:
                            import json
                            chunk = json.loads(line)
                            if 'candidates' in chunk and len(chunk['candidates']) > 0:
                                candidate = chunk['candidates'][0]
                                if 'content' in candidate and 'parts' in candidate['content']:
                                    parts = candidate['content']['parts']
                                    if len(parts) > 0 and 'text' in parts[0]:
                                        yield parts[0]['text']
                        except json.JSONDecodeError:
                            continue
            
            return stream_generator()
            
        except requests.exceptions.RequestException as e:
            print(f"Gemini流式API调用错误: {e}")
            return None
        except Exception as e:
            print(f"Gemini流式API调用异常: {e}")
            return None
    
    def _get_default_params(self) -> dict:
        """获取默认参数"""
        return {
            'max_tokens': 2048,
            'temperature': 0.7,
            'top_p': 1.0,
            'timeout': 60
        }