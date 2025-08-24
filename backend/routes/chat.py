from flask import Blueprint, request, jsonify, Response, current_app
import uuid
import json
from datetime import datetime
from models.models import db, Conversation, Message, ApiKey, Model
from utils.auth import token_required
from ai import AIClient
from utils.constants import DEFAULT_API_PROVIDER

chat_bp = Blueprint('chat', __name__)

def get_active_api_key(provider=DEFAULT_API_PROVIDER):
    """获取活跃的API密钥"""
    return ApiKey.query.filter_by(model_provider=provider, is_active=True).first()

def get_model_provider(model_name):
    """根据模型名称获取提供商"""
    model = Model.query.filter_by(model_name=model_name, is_active=True).first()
    if model:
        return model.model_provider
    # 如果数据库中没有找到，尝试根据模型名称推断
    if 'gpt' in model_name.lower() or 'openai' in model_name.lower():
        return 'openai'
    elif 'claude' in model_name.lower() or 'anthropic' in model_name.lower():
        return 'anthropic'
    elif 'ernie' in model_name.lower() or 'baidu' in model_name.lower():
        return 'baidu'
    elif 'qwen' in model_name.lower() or 'alibaba' in model_name.lower():
        return 'alibaba'
    elif 'glm' in model_name.lower() or 'zhipu' in model_name.lower():
        return 'zhipu'
    else:
        return 'siliconflow'  # 默认使用 siliconflow

@chat_bp.route('/api/chat', methods=['POST'])
@token_required
def chat(current_user):
    """处理聊天请求"""
    data = request.get_json()
    
    # 验证请求数据
    if not data or 'message' not in data or 'model' not in data:
        return jsonify({'error': '缺少必要参数'}), 400
    
    message = data['message']
    model = data['model']
    conversation_id = data.get('conversation_id')
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
    user_id = current_user.id
    
    try:
        # 查找或创建对话
        conversation = Conversation.query.filter_by(conversation_id=conversation_id).first()
        if not conversation:
            conversation = Conversation(
                user_id=user_id,
                conversation_id=conversation_id,
                model=model,
                title=message[:50] + '...' if len(message) > 50 else message
            )
            db.session.add(conversation)
        
        # 保存用户消息
        user_message = Message(
            conversation_id=conversation_id,
            role='user',
            content=message
        )
        db.session.add(user_message)
        
        # 统一的模型API调用逻辑
        # 根据模型获取对应的提供商
        provider = get_model_provider(model)
        api_key_record = get_active_api_key(provider)
        
        if api_key_record and api_key_record.api_key:
            # 提取额外参数，包括stop参数
            extra_params = {}
            if 'stop' in data and data['stop']:
                extra_params['stop'] = data['stop']
            
            ai_response = AIClient.call_ai_api(provider, model, message, api_key_record, **extra_params)
        else:
            ai_response = f"请先在API密钥管理中配置 {provider} 平台的API密钥。"
        
        # 保存AI响应（无推理流的模型仅保存内容）
        ai_message = Message(
            conversation_id=conversation_id,
            role='assistant',
            content=ai_response,
            reasoning=None
        )
        db.session.add(ai_message)
        
        # 更新对话时间
        conversation.updated_at = datetime.utcnow()
        db.session.commit()
        
        from utils.time_utils import to_beijing_iso
        return jsonify({
            'conversation_id': conversation_id,
            'response': ai_response,
            'model': model,
            'timestamp': to_beijing_iso(datetime.utcnow())
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'处理请求时发生错误: {str(e)}'}), 500

@chat_bp.route('/api/chat/stream', methods=['POST'])
@token_required
def chat_stream(current_user):
    """处理流式聊天请求"""
    data = request.get_json()
    
    # 验证请求数据
    if not data or 'message' not in data or 'model' not in data:
        return jsonify({'error': '缺少必要参数'}), 400
    
    message = data['message']
    model = data['model']
    conversation_id = data.get('conversation_id')
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
    user_id = current_user.id
    
    # 在路由函数中获取应用实例
    app = current_app._get_current_object()
    
    def generate_stream():
        with app.app_context():
            try:
                # 查找或创建对话
                conversation = Conversation.query.filter_by(conversation_id=conversation_id).first()
                if not conversation:
                    conversation = Conversation(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        model=model,
                        title=message[:50] + '...' if len(message) > 50 else message
                    )
                    db.session.add(conversation)
                
                # 保存用户消息
                user_message = Message(
                    conversation_id=conversation_id,
                    role='user',
                    content=message
                )
                db.session.add(user_message)
                db.session.commit()
                
                # 发送初始响应
                yield f"data: {json.dumps({'type': 'start', 'conversation_id': conversation_id})}\n\n"
                
                # 统一的流式模型API调用逻辑
                provider = get_model_provider(model)
                api_key_record = get_active_api_key(provider)
                
                if api_key_record and api_key_record.api_key:
                    # 提取额外参数，包括stop参数
                    extra_params = {}
                    if 'stop' in data and data['stop']:
                        extra_params['stop'] = data['stop']
                    
                    # 获取流式响应
                    stream_response = AIClient.call_ai_api(provider, model, message, api_key_record, stream=True, **extra_params)
                    
                    if stream_response:
                        complete_response = ""
                        complete_reasoning = ""
                        
                        # 逐步接收并处理响应
                        for chunk in stream_response:
                            if not chunk.choices:
                                continue
                            
                            # 处理普通内容 - delta.content
                            if chunk.choices[0].delta.content:
                                content = chunk.choices[0].delta.content
                                complete_response += content
                                yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                            
                            # 注意：OpenAI API 的 ChoiceDelta 对象没有 reasoning_content 属性
                            # 如果需要推理功能，需要使用支持推理的模型（如 o1 系列）
                            # 并检查相应的属性名称
                        
                        # 在新的应用上下文中保存数据
                        with app.app_context():
                            # 保存AI响应，推理过程和结果分别存储
                            ai_message = Message(
                                conversation_id=conversation_id,
                                role='assistant',
                                content=complete_response,
                                reasoning=complete_reasoning if complete_reasoning else None
                            )
                            db.session.add(ai_message)
                            
                            # 更新对话时间
                            conversation = Conversation.query.filter_by(conversation_id=conversation_id).first()
                            if conversation:
                                conversation.updated_at = datetime.utcnow()
                            db.session.commit()
                        
                        yield f"data: {json.dumps({'type': 'end', 'complete_response': complete_response, 'complete_reasoning': complete_reasoning})}\n\n"
                    else:
                        error_msg = "流式API调用失败"
                        yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
                else:
                    error_msg = f"请先在API密钥管理中配置 {provider} 平台的API密钥。"
                    yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
                    
            except Exception as e:
                try:
                    with app.app_context():
                        db.session.rollback()
                except:
                    pass  # 忽略rollback错误
                yield f"data: {json.dumps({'type': 'error', 'content': f'处理请求时发生错误: {str(e)}'})}.\n\n"
    
    return Response(
        generate_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization'
        }
    )
