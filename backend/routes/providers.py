from flask import Blueprint, request, jsonify
from models.models import db, Provider
from utils.auth import token_required
from sqlalchemy.exc import IntegrityError

providers_bp = Blueprint('providers', __name__)

@providers_bp.route('/api/providers', methods=['GET'])
@token_required
def get_providers(current_user):
    """获取所有提供商列表"""
    try:
        providers = Provider.get_all_active_providers()
        return jsonify({
            'success': True,
            'data': [provider.to_dict() for provider in providers]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取提供商列表失败: {str(e)}'
        }), 500

@providers_bp.route('/api/providers', methods=['POST'])
@token_required
def create_provider(current_user):
    """创建新的提供商"""
    # 检查用户权限（只有管理员可以创建提供商）
    if current_user.role != 'admin':
        return jsonify({
            'success': False,
            'message': '权限不足，只有管理员可以创建提供商'
        }), 403
    
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['provider_key', 'display_name', 'default_base_url']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'缺少必需字段: {field}'
                }), 400
        
        # 检查provider_key是否已存在
        existing_provider = Provider.query.filter_by(provider_key=data['provider_key']).first()
        if existing_provider:
            return jsonify({
                'success': False,
                'message': f'提供商标识 {data["provider_key"]} 已存在'
            }), 400
        
        # 创建新提供商
        provider = Provider(
            provider_key=data['provider_key'],
            display_name=data['display_name'],
            default_base_url=data['default_base_url'],
            is_active=data.get('is_active', True),
            sort_order=data.get('sort_order', 0)
        )
        
        db.session.add(provider)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '提供商创建成功',
            'data': provider.to_dict()
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '提供商标识已存在'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'创建提供商失败: {str(e)}'
        }), 500

@providers_bp.route('/api/providers/<int:provider_id>', methods=['PUT'])
@token_required
def update_provider(current_user, provider_id):
    """更新提供商信息"""
    # 检查用户权限（只有管理员可以更新提供商）
    if current_user.role != 'admin':
        return jsonify({
            'success': False,
            'message': '权限不足，只有管理员可以更新提供商'
        }), 403
    
    try:
        provider = Provider.query.get(provider_id)
        if not provider:
            return jsonify({
                'success': False,
                'message': '提供商不存在'
            }), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'display_name' in data:
            provider.display_name = data['display_name']
        if 'default_base_url' in data:
            provider.default_base_url = data['default_base_url']
        if 'is_active' in data:
            provider.is_active = data['is_active']
        if 'sort_order' in data:
            provider.sort_order = data['sort_order']
        
        # 检查provider_key是否重复（如果要更新的话）
        if 'provider_key' in data and data['provider_key'] != provider.provider_key:
            existing_provider = Provider.query.filter_by(provider_key=data['provider_key']).first()
            if existing_provider:
                return jsonify({
                    'success': False,
                    'message': f'提供商标识 {data["provider_key"]} 已存在'
                }), 400
            provider.provider_key = data['provider_key']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '提供商更新成功',
            'data': provider.to_dict()
        })
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '提供商标识已存在'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新提供商失败: {str(e)}'
        }), 500

@providers_bp.route('/api/providers/<int:provider_id>', methods=['DELETE'])
@token_required
def delete_provider(current_user, provider_id):
    """删除提供商"""
    # 检查用户权限（只有管理员可以删除提供商）
    if current_user.role != 'admin':
        return jsonify({
            'success': False,
            'message': '权限不足，只有管理员可以删除提供商'
        }), 403
    
    try:
        provider = Provider.query.get(provider_id)
        if not provider:
            return jsonify({
                'success': False,
                'message': '提供商不存在'
            }), 404
        
        # 软删除：设置为不活跃状态
        provider.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '提供商删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'删除提供商失败: {str(e)}'
        }), 500

@providers_bp.route('/api/providers/<int:provider_id>', methods=['GET'])
@token_required
def get_provider(current_user, provider_id):
    """获取单个提供商信息"""
    try:
        provider = Provider.query.get(provider_id)
        if not provider:
            return jsonify({
                'success': False,
                'message': '提供商不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': provider.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取提供商信息失败: {str(e)}'
        }), 500