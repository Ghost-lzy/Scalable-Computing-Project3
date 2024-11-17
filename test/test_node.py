import unittest
from src.node import P2PNode
import threading
import time

class TestP2PNode(unittest.TestCase):
    def setUp(self):
        """初始化两个节点用于测试"""
        self.node1 = P2PNode("1", 5000)
        self.node2 = P2PNode("2", 5001, neighbors=[("127.0.0.1", 5000)])
        threading.Thread(target=self.node1.start).start()
        threading.Thread(target=self.node2.start).start()
        time.sleep(1)  # 等待节点启动

    def tearDown(self):
        """停止节点"""
        self.node1.stop()
        self.node2.stop()

    def test_send_command(self):
        """测试 SEND 命令"""
        self.node2.send_data("127.0.0.1", 5000, {
            "command": "SEND",
            "source": "2",
            "content": "Hello from Node 2"
        })
        time.sleep(1)
        messages = self.node1.get_received_messages()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["content"], "Hello from Node 2")

    def test_broadcast_command(self):
        """测试 BROADCAST 命令"""
        self.node2.broadcast({
            "command": "BROADCAST",
            "source": "2",
            "content": "Broadcast from Node 2"
        })
        time.sleep(1)
        messages = self.node1.get_received_messages()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["content"], "Broadcast from Node 2")

    def test_status_command(self):
        """测试 STATUS 命令"""
        self.node1.handle_status({"command": "STATUS"})

    def test_discover_command(self):
        """测试 DISCOVER 命令"""
        self.node2.handle_discover({"command": "DISCOVER"})

if __name__ == "__main__":
    unittest.main()
