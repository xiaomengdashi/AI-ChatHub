from flask import Flask
from flask_cors import CORS
import uuid
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入配置
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.config import Config
from models.models import db, User
from utils.constants import ROLE_ADMIN, ROLE_USER
from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.conversations import conversations_bp
from routes.apikeys import apikeys_bp
from routes.misc import misc_bp
from routes.users import users_bp
from routes.ai_models import models_bp
from routes.providers import providers_bp

# 导入工具
from sqlalchemy import inspect, text

# 创建Flask应用
def create_app():
    app = Flask(__name__)
    
    # 加载配置
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = Config.SQLALCHEMY_ENGINE_OPTIONS
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    
    # 配置CORS
    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=Config.CORS_SUPPORTS_CREDENTIALS)
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册路由
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(conversations_bp)
    app.register_blueprint(apikeys_bp)
    app.register_blueprint(misc_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(models_bp)
    app.register_blueprint(providers_bp)
    
    return app

# 创建应用实例
app = create_app()

# 初始化数据库和创建默认数据
with app.app_context():
    # 创建数据库表
    db.create_all()
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('message')]
    
    # 检查并添加 reasoning 列（如果不存在）
    try:
        if 'reasoning' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE message ADD COLUMN reasoning TEXT'))
                conn.commit()
            print("已添加 reasoning 列到 message 表")
    except Exception as e:
        print(f"检查/添加 reasoning 列时出错: {e}")
    
    # 创建默认管理员用户（如果不存在）
    if not User.find_by_username('admin'):
        default_admin = User(
            username='admin',
            email='admin@chathub.com',
            api_key=str(uuid.uuid4()),
            subscription_type='premium',
            usage_limit=10000,
            role=ROLE_ADMIN,
            is_active=True
        )
        default_admin.set_password('admin123')  # 默认密码
        db.session.add(default_admin)
        db.session.commit()
        print("创建默认管理员用户: admin (密码: admin123)")
    
    # 创建默认普通用户（如果不存在）
    if not User.find_by_username('user'):
        default_user = User(
            username='user',
            email='user@chathub.com',
            subscription_type='free',
            usage_limit=1000,
            role=ROLE_USER,
            is_active=True
        )
        default_user.set_password('user123')  # 默认密码
        db.session.add(default_user)
        db.session.commit()
        print("创建默认普通用户: user (密码: user123)")

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)