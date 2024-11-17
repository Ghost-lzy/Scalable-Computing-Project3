import hashlib
from cryptography.fernet import Fernet
import base64

# 固定的共享密钥（或通过环境变量/配置文件加载）
SHARED_SECRET = b'some_shared_secret_key_for_demo'  # 示例密钥，实际中建议更复杂
SECRET_KEY = base64.urlsafe_b64encode(hashlib.sha256(SHARED_SECRET).digest())
cipher = Fernet(SECRET_KEY)

def hash_data(data):
    """生成数据的 SHA256 哈希"""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def encrypt_data(data):
    """加密数据并转为 Base64 编码字符串"""
    encrypted_bytes = cipher.encrypt(data.encode('utf-8'))
    return base64.b64encode(encrypted_bytes).decode('utf-8')

def decrypt_data(encoded_data):
    """解码 Base64 并解密数据"""
    encrypted_bytes = base64.b64decode(encoded_data.encode('utf-8'))
    return cipher.decrypt(encrypted_bytes).decode('utf-8')
