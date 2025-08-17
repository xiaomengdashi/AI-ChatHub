#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI API调用示例

这个示例展示了如何使用优化后的OpenAI客户端进行API调用，
相比原始的requests调用，提供了更好的错误处理、参数管理和代码复用性。
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.openai_client import OpenAIClient
from ai import AIClient

def example_direct_client_usage():
    """
    直接使用OpenAI客户端的示例
    """
    print("=== 直接使用OpenAI客户端 ===")
    
    # 初始化客户端
    # 可以使用官方API或兼容的第三方API
    api_key = "sk-XXXX"  # 替换为实际的API密钥
    base_url = "https://api.chatanywhere.tech/v1"  # 或使用官方API: "https://api.openai.com/v1"
    
    client = OpenAIClient(api_key=api_key, base_url=base_url)
    
    # 同步调用示例
    try:
        response = client.call_sync(
            model="gpt-3.5-turbo",  # 或 "gpt-4", "gpt-4o" 等
            message="写一份简单的C++代码",
            system_message="You are a helpful programming assistant.",  # 可选的系统消息
            temperature=0.7,
            max_tokens=1000
        )
        print("同步调用响应:")
        print(response)
        print()
    except Exception as e:
        print(f"同步调用失败: {e}")
    
    # 流式调用示例
    try:
        print("流式调用响应:")
        stream = client.call_stream(
            model="gpt-3.5-turbo",
            message="写一份简单的C++代码",
            system_message="You are a helpful programming assistant.",
            temperature=0.7,
            max_tokens=1000
        )
        
        if stream:
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end='', flush=True)
            print("\n")
        else:
            print("流式调用失败")
    except Exception as e:
        print(f"流式调用失败: {e}")

def example_unified_client_usage():
    """
    使用统一AI客户端接口的示例
    """
    print("=== 使用统一AI客户端接口 ===")
    
    # 模拟API密钥记录对象
    class MockApiKeyRecord:
        def __init__(self, api_key, base_url):
            self.api_key = api_key
            self.base_url = base_url
    
    api_key_record = MockApiKeyRecord(
        api_key="sk-XXXX",  # 替换为实际的API密钥
        base_url="https://api.chatanywhere.tech/v1"
    )
    
    # 同步调用
    try:
        response = AIClient.call_ai_api(
            provider="openai",
            model="gpt-3.5-turbo",
            message="写一份简单的C++代码",
            api_key_or_record=api_key_record,
            stream=False,
            system_message="You are a helpful programming assistant.",
            temperature=0.7,
            max_tokens=1000
        )
        print("统一接口同步调用响应:")
        print(response)
        print()
    except Exception as e:
        print(f"统一接口同步调用失败: {e}")
    
    # 流式调用
    try:
        print("统一接口流式调用响应:")
        stream = AIClient.call_ai_api(
            provider="openai",
            model="gpt-3.5-turbo",
            message="写一份简单的C++代码",
            api_key_or_record=api_key_record,
            stream=True,
            system_message="You are a helpful programming assistant.",
            temperature=0.7,
            max_tokens=1000
        )
        
        if stream:
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end='', flush=True)
            print("\n")
        else:
            print("统一接口流式调用失败")
    except Exception as e:
        print(f"统一接口流式调用失败: {e}")

def example_optimized_parameters():
    """
    展示优化参数使用的示例
    """
    print("=== 优化参数使用示例 ===")
    
    api_key = "sk-XXXX"  # 替换为实际的API密钥
    base_url = "https://api.chatanywhere.tech/v1"
    
    client = OpenAIClient(api_key=api_key, base_url=base_url)
    
    # 使用不同的参数组合
    try:
        # 创意写作参数
        creative_response = client.call_sync(
            model="gpt-3.5-turbo",
            message="写一个关于AI的创意故事",
            temperature=0.9,  # 高创意性
            top_p=0.9,
            max_tokens=500,
            presence_penalty=0.6,  # 鼓励新话题
            frequency_penalty=0.3   # 减少重复
        )
        print("创意写作响应:")
        print(creative_response)
        print()
        
        # 技术问答参数
        technical_response = client.call_sync(
            model="gpt-3.5-turbo",
            message="解释什么是RESTful API",
            system_message="You are a technical expert. Provide accurate and detailed explanations.",
            temperature=0.2,  # 低创意性，更准确
            top_p=0.8,
            max_tokens=800,
            presence_penalty=0.0,
            frequency_penalty=0.0
        )
        print("技术问答响应:")
        print(technical_response)
        print()
        
    except Exception as e:
        print(f"优化参数调用失败: {e}")

def main():
    """
    主函数，运行所有示例
    """
    print("OpenAI API调用优化示例")
    print("=" * 50)
    print()
    
    # 注意：运行前请替换API密钥
    print("注意：运行前请在代码中替换实际的API密钥！")
    print()
    
    # 运行示例（注释掉以避免实际API调用）
    # example_direct_client_usage()
    # example_unified_client_usage()
    # example_optimized_parameters()
    
    print("示例代码已准备就绪，请替换API密钥后取消注释运行。")

if __name__ == "__main__":
    main()