import unittest
from src.utils import hash_data, encrypt_data, decrypt_data

class TestUtils(unittest.TestCase):
    def test_hash_data(self):
        """测试数据哈希"""
        data = "hello world"
        hashed = hash_data(data)
        self.assertEqual(len(hashed), 64)  # SHA256 哈希长度为 64 字符

    def test_encrypt_decrypt_data(self):
        """测试数据加密和解密"""
        data = "secret message"
        encrypted = encrypt_data(data)
        decrypted = decrypt_data(encrypted)
        self.assertEqual(decrypted, data)

if __name__ == "__main__":
    unittest.main()
