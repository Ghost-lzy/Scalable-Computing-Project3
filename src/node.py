import socket
import threading
import json
from queue import Queue
from src.utils import encrypt_data, decrypt_data


class P2PNode:
    def __init__(self, node_id, port):
        """
        Initialize the P2P node
        :param node_id: Unique identifier for the node
        :param port: Port on which the node listens
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
        """Get the local IP address"""
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)

    def start(self, bootstrap_ip=None, bootstrap_port=None):
        """
        Start the node, listen on the port, and initialize neighbors
        :param bootstrap_ip: IP address of the bootstrap node
        :param bootstrap_port: Port of the bootstrap node
        """
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)
        self.running = True
        print(f"Node {self.node_id} started on {self.ip}:{self.port}.")
        threading.Thread(target=self.listen_for_connections, daemon=True).start()

        # If there is a bootstrap node, try to join the network
        if bootstrap_ip and bootstrap_port:
            self.join_network(bootstrap_ip, bootstrap_port)

    def listen_for_connections(self):
        """Listen for connection requests from other nodes"""
        while self.running:
            conn, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_connection, args=(conn, addr), daemon=True).start()

    def handle_connection(self, conn, addr):
        """Handle received connections"""
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
        Join the network: send own information to the bootstrap node
        :param bootstrap_ip: IP address of the bootstrap node
        :param bootstrap_port: Port of the bootstrap node
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
        Handle NEW_NODE command: update neighbor list and trigger network-wide update
        """
        node_id = message.get("node_id")
        ip = message.get("ip")
        port = message.get("port")
        new_neighbor = (ip, port)

        if new_neighbor not in self.neighbors:
            print(f"Node {self.node_id} detected new node: {node_id} at {ip}:{port}")
            self.neighbors.append(new_neighbor)

        # Broadcast the latest network neighbor information to all neighbors
        self.broadcast_update_neighbors()

    def broadcast_update_neighbors(self, exclude_self=False):
        """
        Broadcast the latest neighbor information to the network
        :param exclude_self: Whether to remove the current node from the list
        """
        updated_neighbors = self.neighbors
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
        Handle UPDATE_NEIGHBORS command: overwrite the neighbor list
        """
        updated_neighbors = [tuple(neighbor) for neighbor in message.get("neighbors", [])]
        self_ip_port = (self.ip, self.port)
        # Remove duplicates and exclude self
        self.neighbors = list(set(updated_neighbors) - {self_ip_port})
        print(f"Node {self.node_id} updated neighbors: {self.neighbors}")

    def send_data(self, target_ip, target_port, data):
        """Send data to the target node"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((target_ip, target_port))
            sock.sendall(json.dumps(data).encode('utf-8'))
            sock.close()
        except Exception as e:
            print(f"Error sending data to {target_ip}:{target_port} - {e}")

    def send_message(self, target_ip, target_port, content):
        """Package and send the SEND command"""
        encrypted_content = encrypt_data(content)
        self.send_data(target_ip, target_port, {
            "command": "SEND",
            "source": self.node_id,
            "content": encrypted_content
        })

    def broadcast(self, content):
        """Package and broadcast the BROADCAST command"""
        encrypted_content = encrypt_data(content)
        # Print neighbors before broadcasting
        print(f"Node {self.node_id} broadcasting to neighbors: {self.neighbors}")
        for neighbor_ip, neighbor_port in self.neighbors:
            self.send_data(neighbor_ip, neighbor_port, {
                "command": "BROADCAST",
                "source": self.node_id,
                "content": encrypted_content
            })

    def handle_send(self, message):
        """Handle SEND command"""
        source = message.get("source")
        encrypted_content = message.get("content")
        content = decrypt_data(encrypted_content)
        print(f"Node {self.node_id} received message from {source}: {content}")

    def handle_broadcast(self, message):
        """Handle BROADCAST command"""
        source = message.get("source")
        encrypted_content = message.get("content")
        content = decrypt_data(encrypted_content)
        print(f"Node {self.node_id} received broadcast from {source}: {content}")

        # The implementation has issues, temporarily commented out
        # # Forward the broadcast message to other neighbors
        # for neighbor_ip, neighbor_port in self.neighbors:
        #     # Exclude the source node
        #     if (neighbor_ip, neighbor_port) != (self.ip, self.port):
        #         self.send_data(neighbor_ip, neighbor_port, message)

    def handle_status(self, message):
        """Handle STATUS command"""
        print(f"Node {self.node_id} reporting status: Running on {self.ip}:{self.port}, neighbors: {self.neighbors}")

    def handle_discover(self, message):
        """Handle DISCOVER command"""
        print(f"Node {self.node_id} discovered neighbors: {self.neighbors}")

    def get_received_messages(self):
        """Get the queue of received messages"""
        messages = []
        while not self.received_queue.empty():
            messages.append(self.received_queue.get())
        return messages

    def stop(self):
        """
        Stop the node and notify neighbors to update the topology
        """
        print(f"Node {self.node_id} stopping...")
        # Broadcast exit message to let neighbors update the topology
        self.broadcast_update_neighbors(exclude_self=True)

        self.running = False
        self.server_socket.close()
        print(f"Node {self.node_id} stopped.")