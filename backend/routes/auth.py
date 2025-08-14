from flask import Blueprint, request, jsonify
from datetime import datetime, timezone, timedelta
import jwt
import uuid
from models.models import User, db
from utils.auth import token_required, admin_required
from models.config import Config
from utils.email_verification import get_email_verifier
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """普通用户注册（需要邮箱验证码）"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        verification_code = data.get('verification_code')
        
        if not username or not email or not password or not verification_code:
            return jsonify({'error': '用户名、邮箱、密码和验证码不能为空'}), 400
        
        # 验证用户名长度
        if len(username) < 3 or len(username) > 20:
            return jsonify({'error': '用户名长度必须在3-20个字符之间'}), 400
        
        # 验证密码长度
        if len(password) < 6:
            return jsonify({'error': '密码长度至少6个字符'}), 400
        
        # 检查用户名是否已存在
        if User.username_exists(username):
            return jsonify({'error': '用户名已存在'}), 400
        
        # 检查邮箱是否已存在
        if User.email_exists(email):
            return jsonify({'error': '邮箱已存在'}), 400
        
        # 验证邮箱验证码
        try:
            email_verifier = get_email_verifier()
            code_valid, code_message = email_verifier.verify_code(email, verification_code)
            
            if not code_valid:
                logger.warning(f"Registration failed for {email}: {code_message}")
                return jsonify({'error': code_message}), 400
                
        except ValueError as e:
            logger.error(f"Email verifier configuration error during registration: {str(e)}")
            return jsonify({'error': '邮箱服务配置错误，请联系管理员'}), 500
        
        # 创建新用户（普通用户角色，邮箱已验证）
        new_user = User(
            username=username,
            email=email,
            role='user',
            api_key=str(uuid.uuid4()),  # 为每个用户生成唯一的API key
            subscription_type='free',
            usage_count=0,
            usage_limit=100,
            is_active=True,
            email_verified=True  # 注册时已验证邮箱
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '注册成功！请使用您的账户登录',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'role': new_user.role
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/send-verification-code', methods=['POST'])
def send_verification_code():
    """发送邮箱验证码"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': '邮箱地址不能为空'}), 400
        
        # 验证邮箱格式
        import re
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, email):
            return jsonify({'error': '请输入有效的邮箱地址'}), 400
        
        # 检查邮箱是否已被注册
        if User.email_exists(email):
            return jsonify({'error': '该邮箱已被注册'}), 400
        
        # 发送验证码
        try:
            email_verifier = get_email_verifier()
            success, message = email_verifier.send_verification_code(email)
            
            if success:
                logger.info(f"Verification code sent to {email}")
                return jsonify({
                    'success': True,
                    'message': '验证码已发送到您的邮箱，请查收'
                })
            else:
                logger.warning(f"Failed to send verification code to {email}: {message}")
                return jsonify({'error': message}), 400
                
        except ValueError as e:
            logger.error(f"Email verifier configuration error: {str(e)}")
            return jsonify({'error': '邮箱服务配置错误，请联系管理员'}), 500
            
    except Exception as e:
        logger.error(f"Error sending verification code: {str(e)}")
        return jsonify({'error': '发送验证码失败，请稍后重试'}), 500

@auth_bp.route('/api/auth/verify-email-code', methods=['POST'])
def verify_email_code():
    """验证邮箱验证码"""
    try:
        data = request.get_json()
        email = data.get('email')
        code = data.get('code')
        
        if not email or not code:
            return jsonify({'error': '邮箱和验证码不能为空'}), 400
        
        # 验证验证码
        try:
            email_verifier = get_email_verifier()
            success, message = email_verifier.verify_code(email, code)
            
            if success:
                logger.info(f"Email verification successful for {email}")
                return jsonify({
                    'success': True,
                    'message': message
                })
            else:
                logger.warning(f"Email verification failed for {email}: {message}")
                return jsonify({'error': message}), 400
                
        except ValueError as e:
            logger.error(f"Email verifier configuration error: {str(e)}")
            return jsonify({'error': '邮箱服务配置错误，请联系管理员'}), 500
            
    except Exception as e:
        logger.error(f"Error verifying email code: {str(e)}")
        return jsonify({'error': '验证失败，请稍后重试'}), 500

@auth_bp.route('/api/auth/admin/register', methods=['POST'])
@admin_required
def admin_register(current_user):
    """管理员注册新用户"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')
        
        if not username or not email or not password:
            return jsonify({'error': '用户名、邮箱和密码不能为空'}), 400
        
        # 检查用户名是否已存在
        if User.username_exists(username):
            return jsonify({'error': '用户名已存在'}), 400
        
        # 检查邮箱是否已存在
        if User.email_exists(email):
            return jsonify({'error': '邮箱已存在'}), 400
        
        # 创建新用户
        new_user = User(
            username=username,
            email=email,
            role=role,
            api_key=str(uuid.uuid4()) if role == 'admin' else None
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '用户注册成功',
            'user': new_user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400
        
        # 从数据库查找用户
        user = User.find_by_username(username)
        
        # 验证用户和密码
        if user and user.is_active and user.check_password(password):
            # 生成JWT令牌
            token = jwt.encode({
                'username': username,
                'user_id': user.id,
                'role': user.role,
                'exp': datetime.now(timezone.utc) + timedelta(hours=24)
            }, Config.SECRET_KEY, algorithm='HS256')
            
            return jsonify({
                'success': True,
                'token': token,
                'user': user.to_dict(include_sensitive=(user.role == 'admin')),
                'message': '登录成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误，或账户已被禁用'
            }), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    """验证令牌有效性"""
    return jsonify({
        'valid': True,
        'user': current_user.to_dict(include_sensitive=(current_user.role == 'admin'))
    })

@auth_bp.route('/api/auth/logout', methods=['POST'])
@token_required
def logout(current_user):
    """用户登出"""
    return jsonify({'message': '登出成功'})