#!/usr/bin/env python3
"""
初始化默认数据
包括提供商和模型数据的初始化
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.models import db, Provider, Model

# 提供商信息映射
PROVIDER_INFO_MAP = {
    'openai': {
        'display_name': 'OpenAI',
        'default_base_url': 'https://api.openai.com/v1'
    },
    'anthropic': {
        'display_name': 'Anthropic',
        'default_base_url': 'https://api.anthropic.com/v1'
    },
    'google': {
        'display_name': 'Gemini',
        'default_base_url': 'https://generativelanguage.googleapis.com/v1'
    },
    'baidu': {
        'display_name': '文心一言',
        'default_base_url': 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1'
    },
    'alibaba': {
        'display_name': '阿里云百炼',
        'default_base_url': 'https://dashscope.aliyuncs.com/api/v1'
    },
    'siliconflow': {
        'display_name': '硅基流动',
        'default_base_url': 'https://api.siliconflow.cn/v1'
    },
    'deepseek': {
        'display_name': 'DeepSeek',
        'default_base_url': 'https://api.deepseek.com/v1'
    },
    'moonshot': {
        'display_name': '月之暗面',
        'default_base_url': 'https://api.moonshot.cn/v1'
    },
    'baichuan': {
        'display_name': '百川智能',
        'default_base_url': 'https://api.baichuan-ai.com/v1'
    },
    'zhipu': {
        'display_name': '智谱AI',
        'default_base_url': 'https://open.bigmodel.cn/api/paas/v4'
    },
    'qwen': {
        'display_name': '通义千问',
        'default_base_url': 'https://dashscope.aliyuncs.com/api/v1'
    },
    'doubao': {
        'display_name': '火山引擎',
        'default_base_url': 'https://ark.cn-beijing.volces.com/api/v3'
    }
}

def init_providers():
    """初始化提供商数据"""
    # 检查是否已经有提供商数据
    existing_count = Provider.query.count()
    if existing_count > 0:
        print(f"提供商表中已有 {existing_count} 条记录，跳过初始化")
        return
    
    print("开始初始化提供商数据...")
    
    sort_order = 0
    for provider_key, info in PROVIDER_INFO_MAP.items():
        provider = Provider(
            provider_key=provider_key,
            display_name=info['display_name'],
            default_base_url=info['default_base_url'],
            is_active=True,
            sort_order=sort_order
        )
        db.session.add(provider)
        sort_order += 10
        print(f"添加提供商: {provider_key} - {info['display_name']}")
    
    try:
        db.session.commit()
        print(f"成功初始化 {len(PROVIDER_INFO_MAP)} 个提供商")
    except Exception as e:
        db.session.rollback()
        print(f"初始化提供商失败: {e}")
        raise

def init_default_models():
    """初始化默认模型数据"""
    # 检查是否已有模型数据
    existing_models = Model.query.count()
    if existing_models > 0:
        print(f"数据库中已有 {existing_models} 个模型，跳过初始化")
        return
    
    # 默认模型列表
    default_models = [
        {
            'model_name': 'Qwen/QwQ-32B',
            'display_name': 'QwQ-32B',
            'model_provider': 'siliconflow',
            'model_type': 'chat',
            'max_tokens': 32768,
            'supports_streaming': True,
            'supports_function_calling': True,
            'supports_vision': False,
            'input_price_per_1k': 0.001,
            'output_price_per_1k': 0.002,
            'description': '通义千问QwQ-32B模型，支持32K上下文长度',
            'is_active': True,
            'sort_order': 1
        },
        {
            'model_name': 'gpt-4o',
            'display_name': 'GPT-4o',
            'model_provider': 'openai',
            'model_type': 'chat',
            'max_tokens': 128000,
            'supports_streaming': True,
            'supports_function_calling': True,
            'supports_vision': True,
            'input_price_per_1k': 0.005,
            'output_price_per_1k': 0.015,
            'description': 'OpenAI GPT-4o模型，支持视觉和函数调用',
            'is_active': True,
            'sort_order': 2
        },
        {
            'model_name': 'gpt-4o-mini',
            'display_name': 'GPT-4o Mini',
            'model_provider': 'openai',
            'model_type': 'chat',
            'max_tokens': 128000,
            'supports_streaming': True,
            'supports_function_calling': True,
            'supports_vision': True,
            'input_price_per_1k': 0.00015,
            'output_price_per_1k': 0.0006,
            'description': 'OpenAI GPT-4o Mini模型，性价比更高',
            'is_active': True,
            'sort_order': 3
        },
        {
            'model_name': 'claude-3-5-sonnet-20241022',
            'display_name': 'Claude-3.5 Sonnet',
            'model_provider': 'anthropic',
            'model_type': 'chat',
            'max_tokens': 200000,
            'supports_streaming': True,
            'supports_function_calling': True,
            'supports_vision': True,
            'input_price_per_1k': 0.003,
            'output_price_per_1k': 0.015,
            'description': 'Anthropic Claude-3.5 Sonnet模型，支持200K上下文',
            'is_active': True,
            'sort_order': 4
        },
        {
            'model_name': 'claude-3-haiku-20240307',
            'display_name': 'Claude-3 Haiku',
            'model_provider': 'anthropic',
            'model_type': 'chat',
            'max_tokens': 200000,
            'supports_streaming': True,
            'supports_function_calling': False,
            'supports_vision': True,
            'input_price_per_1k': 0.00025,
            'output_price_per_1k': 0.00125,
            'description': 'Anthropic Claude-3 Haiku模型，快速且经济',
            'is_active': True,
            'sort_order': 5
        },
        {
            'model_name': 'gemini-1.5-pro',
            'display_name': 'Gemini 1.5 Pro',
            'model_provider': 'google',
            'model_type': 'chat',
            'max_tokens': 2000000,
            'supports_streaming': True,
            'supports_function_calling': True,
            'supports_vision': True,
            'input_price_per_1k': 0.00125,
            'output_price_per_1k': 0.005,
            'description': 'Google Gemini 1.5 Pro模型，支持2M上下文',
            'is_active': True,
            'sort_order': 6
        },
        {
            'model_name': 'gemini-1.5-flash',
            'display_name': 'Gemini 1.5 Flash',
            'model_provider': 'google',
            'model_type': 'chat',
            'max_tokens': 1000000,
            'supports_streaming': True,
            'supports_function_calling': True,
            'supports_vision': True,
            'input_price_per_1k': 0.000075,
            'output_price_per_1k': 0.0003,
            'description': 'Google Gemini 1.5 Flash模型，快速且经济',
            'is_active': True,
            'sort_order': 7
        }
    ]
    
    # 创建模型记录
    for model_data in default_models:
        model = Model(**model_data)
        db.session.add(model)
    
    try:
        db.session.commit()
        print(f"成功初始化 {len(default_models)} 个默认模型")
        
        # 显示创建的模型
        for model_data in default_models:
            print(f"  - {model_data['display_name']} ({model_data['model_name']})")
            
    except Exception as e:
        db.session.rollback()
        print(f"初始化模型失败: {e}")
        raise

def init_all_data():
    """初始化所有数据"""
    app = create_app()
    
    with app.app_context():
        print("开始初始化数据...")
        
        # 先初始化提供商
        init_providers()
        
        # 再初始化模型
        init_default_models()
        
        print("数据初始化完成！")

if __name__ == '__main__':
    init_all_data()