import smtplib
import random
import string
import time
import logging
import re
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.header import Header
from typing import Tuple, Optional, Dict, Any
from models.config import Config

# 配置日志
logger = logging.getLogger("EmailVerification")

class EmailVerification:
    def __init__(self, 
                 smtp_server: str = None, 
                 smtp_port: int = None, 
                 sender_email: str = None, 
                 sender_password: str = None, 
                 sender_name: str = "ChatHub注册系统",
                 code_expiry_minutes: int = 5,
                 max_send_attempts: int = 3,
                 retry_delay_seconds: int = 3,
                 rate_limit_seconds: int = 60):
        """初始化邮箱验证码发送器"""
        # 从配置文件获取邮箱设置
        self.smtp_server = smtp_server or getattr(Config, 'SMTP_SERVER', 'smtp.163.com')
        self.smtp_port = smtp_port or getattr(Config, 'SMTP_PORT', 465)
        self.sender_email = sender_email or getattr(Config, 'SENDER_EMAIL', '')
        self.sender_password = sender_password or getattr(Config, 'SENDER_PASSWORD', '')
        
        # 验证邮箱配置
        if not self.sender_email or not self.sender_password:
            raise ValueError("邮箱配置不完整，请检查SENDER_EMAIL和SENDER_PASSWORD配置")
            
        # 验证邮箱格式
        if not self._is_valid_email(self.sender_email):
            raise ValueError("发送者邮箱格式无效")
            
        self.sender_name = sender_name
        self.code_expiry = code_expiry_minutes
        self.max_attempts = max_send_attempts
        self.retry_delay = retry_delay_seconds
        self.rate_limit = rate_limit_seconds
        
        # 存储验证码信息和发送记录（生产环境建议使用Redis）
        self.verification_codes: Dict[str, Dict[str, Any]] = {}
        self.send_records: Dict[str, float] = {}
        
    def _is_valid_email(self, email: str) -> bool:
        """验证邮箱格式是否有效"""
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email) is not None
    
    def generate_verification_code(self, length: int = 6) -> str:
        """生成随机数字验证码"""
        return ''.join(random.choice(string.digits) for _ in range(length))
    
    def is_within_rate_limit(self, email: str) -> Tuple[bool, Optional[str]]:
        """检查是否在频率限制内"""
        last_sent = self.send_records.get(email)
        if last_sent:
            elapsed = time.time() - last_sent
            if elapsed < self.rate_limit:
                remaining = int(self.rate_limit - elapsed)
                return False, f"发送过于频繁，请{remaining}秒后再试"
        return True, None
    
    def store_verification_code(self, email: str, code: str) -> None:
        """存储验证码及过期时间"""
        expiry_time = datetime.now() + timedelta(minutes=self.code_expiry)
        self.verification_codes[email] = {
            "code": code,
            "expiry_time": expiry_time,
            "created_at": datetime.now()
        }
        logger.info(f"Stored verification code for {email}, expires at {expiry_time}")
    
    def verify_code(self, email: str, code: str) -> Tuple[bool, str]:
        """验证验证码是否有效"""
        if email not in self.verification_codes:
            return False, "未找到验证码，请重新获取"
            
        record = self.verification_codes[email]
        
        if datetime.now() > record["expiry_time"]:
            del self.verification_codes[email]
            return False, f"验证码已过期，请重新获取（有效期{self.code_expiry}分钟）"
            
        if record["code"] != code:
            return False, "验证码不正确"
            
        del self.verification_codes[email]
        return True, "验证码验证成功"
    
    def _format_from_header(self) -> str:
        """严格按照RFC标准格式化From头信息"""
        try:
            # 对发送者名称进行编码，确保符合RFC2047标准
            encoded_name = Header(self.sender_name, 'utf-8').encode()
            # 确保格式为 "编码后的名称 <邮箱地址>"
            return f"{encoded_name} <{self.sender_email}>"
        except Exception as e:
            logger.warning(f"Failed to encode sender name: {str(e)}, using default")
            # 出错时使用仅包含邮箱的简化格式
            return f"<{self.sender_email}>"
    
    def send_verification_code(self, receiver_email: str, code: Optional[str] = None) -> Tuple[bool, str]:
        """发送验证码到指定邮箱，完全符合RFC标准"""
        # 验证接收邮箱格式
        if not self._is_valid_email(receiver_email):
            return False, "接收邮箱格式无效"
            
        # 检查频率限制
        rate_limit_ok, rate_limit_msg = self.is_within_rate_limit(receiver_email)
        if not rate_limit_ok:
            logger.warning(f"Rate limit hit for {receiver_email}: {rate_limit_msg}")
            return False, rate_limit_msg
            
        # 生成验证码
        if code is None:
            code = self.generate_verification_code()
        
        # 邮件内容 - 避免使用特殊字符
        subject = "ChatHub注册验证码"
        content = f"""您好！

您正在注册ChatHub账户，您的验证码是：{code}

验证码有效期为{self.code_expiry}分钟，请在有效期内完成验证。

如非本人操作，请忽略此邮件。

祝您使用愉快！
ChatHub团队"""
        
        # 创建邮件消息
        message = MIMEText(content, 'plain', 'utf-8')
        
        # 严格按照RFC标准设置所有头部信息
        message['From'] = self._format_from_header()
        message['To'] = receiver_email
        message['Subject'] = Header(subject, 'utf-8').encode()  # 确保主题正确编码
        message['Reply-To'] = self.sender_email
        message['X-Mailer'] = 'ChatHub Email Service'
        message['MIME-Version'] = '1.0'
        message['Content-Transfer-Encoding'] = '8bit'
        
        # 生成符合RFC标准的Message-ID
        domain = self.sender_email.split('@')[-1] if '@' in self.sender_email else 'chathub.com'
        message['Message-ID'] = f"<{random.getrandbits(64)}.{int(time.time())}@{domain}>"
        
        # 尝试发送邮件
        for attempt in range(1, self.max_attempts + 1):
            try:
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=10) as server:
                    server.login(self.sender_email, self.sender_password)
                    # 确保发送者与登录邮箱一致
                    server.sendmail(self.sender_email, receiver_email, message.as_string())
                
                # 更新记录
                self.send_records[receiver_email] = time.time()
                self.store_verification_code(receiver_email, code)
                
                logger.info(f"Verification code sent to {receiver_email} (attempt {attempt})")
                return True, "验证码发送成功"
                
            except smtplib.SMTPAuthenticationError:
                logger.error("SMTP authentication failed - check credentials")
                return False, "邮箱认证失败，请检查邮箱配置"
                
            except smtplib.SMTPConnectError:
                if attempt < self.max_attempts:
                    logger.warning(f"Connection failed (attempt {attempt}), retrying...")
                    time.sleep(self.retry_delay)
                    continue
                logger.error("Failed to connect to SMTP server")
                return False, "无法连接到邮件服务器，请检查网络连接"
                
            except smtplib.SMTPResponseException as e:
                logger.error(f"SMTP server rejected request: {e.smtp_code} - {e.smtp_error.decode()}")
                return False, f"邮件服务器拒绝请求: {e.smtp_code}"
                
            except smtplib.SMTPException as e:
                logger.error(f"SMTP error occurred: {str(e)}")
                return False, f"邮件发送失败: {str(e)}"
                
            except Exception as e:
                if attempt < self.max_attempts:
                    logger.warning(f"Unexpected error (attempt {attempt}): {str(e)}, retrying...")
                    time.sleep(self.retry_delay)
                    continue
                logger.error(f"Unexpected error: {str(e)}")
                return False, f"发生错误: {str(e)}"
        
        return False, f"已尝试{self.max_attempts}次，仍无法发送邮件，请稍后再试"
    
    def clean_expired_codes(self) -> int:
        """清理过期的验证码"""
        now = datetime.now()
        expired = [email for email, record in self.verification_codes.items() 
                  if now > record["expiry_time"]]
        
        for email in expired:
            del self.verification_codes[email]
            
        if expired:
            logger.info(f"Cleaned {len(expired)} expired verification codes")
        return len(expired)

# 全局邮箱验证实例
_email_verifier = None

def get_email_verifier() -> EmailVerification:
    """获取邮箱验证实例（单例模式）"""
    global _email_verifier
    if _email_verifier is None:
        try:
            _email_verifier = EmailVerification()
        except ValueError as e:
            logger.error(f"Failed to initialize email verifier: {str(e)}")
            raise
    return _email_verifier