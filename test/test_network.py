import unittest
from src.network import P2PNetwork

class TestP2PNetwork(unittest.TestCase):
    def setUp(self):
        """初始化网络管理模块"""
        self.network = P2PNetwork()

    def test_register_node(self):
        """测试节点注册"""
        self.network.register_node("1", "127.0.0.1", 5000)
        self.assertIn("1", self.network.nodes)
        self.assertEqual(self.network.nodes["1"], ("127.0.0.1", 5000))

    def test_discover_neighbors(self):
        """测试发现邻居"""
        self.network.register_node("1", "127.0.0.1", 5000)
        self.network.register_node("2", "127.0.0.1", 5001)
        neighbors = self.network.discover_neighbors("1")
        self.assertEqual(len(neighbors), 1)
        self.assertEqual(neighbors[0], ("127.0.0.1", 5001))

if __name__ == "__main__":
    unittest.main()
