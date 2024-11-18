import socket
import threading
import json
from queue import Queue
from src.utils import encrypt_data, decrypt_data


class P2PNode:
    def __init__(self, node_id, port):
        """
        初始化 P2P 节点
        :param node_id: 节点唯一标识
        :param port: 节点监听的端口
        """
        self.node_id = node_id
        self.ip = self.get_local_ip()
        self.port = port
        self.neighbors = []  # [(IP, Port)]
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False
        self.received_queue = Queue()
        self.commands = {
            "SEND": self.handle_send,
            "BROADCAST": self.handle_broadcast,
            "STATUS": self.handle_status,
            "DISCOVER": self.handle_discover,
            "NEW_NODE": self.handle_new_node,
            "UPDATE_NEIGHBORS": self.handle_update_neighbors,
        }

    def get_local_ip(self):
        """获取本机的局域网 IP 地址"""
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)

    def start(self, bootstrap_ip=None, bootstrap_port=None):
        """
        启动节点，监听端口并初始化邻居
        :param bootstrap_ip: 引导节点的 IP 地址
        :param bootstrap_port: 引导节点的端口
        """
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)
        self.running = True
        print(f"Node {self.node_id} started on {self.ip}:{self.port}.")
        threading.Thread(target=self.listen_for_connections, daemon=True).start()

        # 如果有引导节点，尝试加入网络
        if bootstrap_ip and bootstrap_port:
            self.join_network(bootstrap_ip, bootstrap_port)

    def listen_for_connections(self):
        """监听其他节点的连接请求"""
        while self.running:
            conn, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_connection, args=(conn, addr), daemon=True).start()

    def handle_connection(self, conn, addr):
        """处理收到的连接"""
        data = conn.recv(1024).decode('utf-8')
        if data:
            message = json.loads(data)
            command = message.get("command")
            if command in self.commands:
                self.commands[command](message)
            else:
                print(f"Unknown command received: {command}")
            self.received_queue.put(message)
        conn.close()

    def join_network(self, bootstrap_ip, bootstrap_port):
        """
        加入网络：向引导节点发送自己的信息
        :param bootstrap_ip: 引导节点的 IP 地址
        :param bootstrap_port: 引导节点的端口
        """
        print(f"Node {self.node_id} joining network via bootstrap node at {bootstrap_ip}:{bootstrap_port}")
        self.send_data(bootstrap_ip, bootstrap_port, {
            "command": "NEW_NODE",
            "node_id": self.node_id,
            "ip": self.ip,
            "port": self.port,
        })

    def handle_new_node(self, message):
        """
        处理 NEW_NODE 命令：更新邻居列表并触发全网更新
        """
        node_id = message.get("node_id")
        ip = message.get("ip")
        port = message.get("port")
        new_neighbor = (ip, port)

        if new_neighbor not in self.neighbors:
            print(f"Node {self.node_id} detected new node: {node_id} at {ip}:{port}")
            self.neighbors.append(new_neighbor)

        # 向所有邻居广播最新的全网邻居信息
        self.broadcast_update_neighbors()

    def broadcast_update_neighbors(self, exclude_self=False):
        """
        广播全网最新邻居信息
        :param exclude_self: 是否从列表中移除当前节点
        """
        updated_neighbors = self.neighbors + [(self.ip, self.port)]
        if not exclude_self:
            updated_neighbors.append((self.ip, self.port))

        update_message = {
            "command": "UPDATE_NEIGHBORS",
            "neighbors": updated_neighbors
        }
        for neighbor_ip, neighbor_port in self.neighbors:
            self.send_data(neighbor_ip, neighbor_port, update_message)

    def handle_update_neighbors(self, message):
        """
        处理 UPDATE_NEIGHBORS 命令：覆盖邻居列表
        """
        updated_neighbors = [tuple(neighbor) for neighbor in message.get("neighbors", [])]
        self_ip_port = (self.ip, self.port)
        # 去重并排除自己
        self.neighbors = list(set(updated_neighbors) - {self_ip_port})
        print(f"Node {self.node_id} updated neighbors: {self.neighbors}")

    def send_data(self, target_ip, target_port, data):
        """向目标节点发送数据"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((target_ip, target_port))
            sock.sendall(json.dumps(data).encode('utf-8'))
            sock.close()
        except Exception as e:
            print(f"Error sending data to {target_ip}:{target_port} - {e}")

    def send_message(self, target_ip, target_port, content):
        """封装 SEND 命令并发送"""
        encrypted_content = encrypt_data(content)
        self.send_data(target_ip, target_port, {
            "command": "SEND",
            "source": self.node_id,
            "content": encrypted_content
        })

    def broadcast(self, content):
        """封装 BROADCAST 命令并广播"""
        encrypted_content = encrypt_data(content)
        # 打印广播钱的neighbors:
        print(f"Node {self.node_id} broadcasting to neighbors: {self.neighbors}")
        for neighbor_ip, neighbor_port in self.neighbors:
            self.send_data(neighbor_ip, neighbor_port, {
                "command": "BROADCAST",
                "source": self.node_id,
                "content": encrypted_content
            })

    def handle_send(self, message):
        """处理 SEND 命令"""
        source = message.get("source")
        encrypted_content = message.get("content")
        content = decrypt_data(encrypted_content)
        print(f"Node {self.node_id} received message from {source}: {content}")

    def handle_broadcast(self, message):
        """处理 BROADCAST 命令"""
        source = message.get("source")
        encrypted_content = message.get("content")
        content = decrypt_data(encrypted_content)
        print(f"Node {self.node_id} received broadcast from {source}: {content}")

        # 实现有问题，暂时注释掉
        # # 转发广播消息给其他邻居
        # for neighbor_ip, neighbor_port in self.neighbors:
        #     # 不可包含source节点
        #     if (neighbor_ip, neighbor_port) != (self.ip, self.port):
        #         self.send_data(neighbor_ip, neighbor_port, message)

    def handle_status(self, message):
        """处理 STATUS 命令"""
        print(f"Node {self.node_id} reporting status: Running on {self.ip}:{self.port}, neighbors: {self.neighbors}")

    def handle_discover(self, message):
        """处理 DISCOVER 命令"""
        print(f"Node {self.node_id} discovered neighbors: {self.neighbors}")

    def get_received_messages(self):
        """获取收到的消息队列"""
        messages = []
        while not self.received_queue.empty():
            messages.append(self.received_queue.get())
        return messages

    def stop(self):
        """
        停止节点并通知邻居更新拓扑
        """
        print(f"Node {self.node_id} stopping...")
        # 广播退出消息，让邻居更新拓扑
        self.broadcast_update_neighbors(exclude_self=True)

        self.running = False
        self.server_socket.close()
        print(f"Node {self.node_id} stopped.")
