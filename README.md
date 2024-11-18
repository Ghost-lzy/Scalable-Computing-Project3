
# P2P Node Network

This project implements a simple peer-to-peer (P2P) network where nodes can communicate with each other, send messages, broadcast messages, and discover other nodes in the network.

## Requirements

- Python 3.7 or higher

## Installation

1. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Starting a Node

To start a node, run the following command:
```sh
python main.py <node_id> <port> [bootstrap_ip bootstrap_port]
```

- `<node_id>`: A unique identifier for the node.
- `<port>`: The port number on which the node will listen for connections.
- `[bootstrap_ip]` (optional): The IP address of an existing node to join the network.
- `[bootstrap_port]` (optional): The port number of the existing node to join the network.

### Example

Start the first node:
```sh
python main.py node1 6000
```

Start a second node and join the network via the first node:
```sh
python main.py node2 6001 <node1_ip> 6000
```

### Commands

Once a node is running, you can interact with it using the following commands:

- `EXIT`: Stop the node.
- `SEND <target_ip> <target_port> <content>`: Send a message to a specific node.
- `BROADCAST <content>`: Broadcast a message to all neighbors.
- `DISCOVER`: Discover and print the list of neighbors.
- `STATUS`: Print the current status of the node.

### Example Commands

1. **Send a message to a specific node**:
    ```sh
    SEND <target_ip> 6001 Hello! This is Node 1.
    ```

2. **Broadcast a message to all neighbors**:
    ```sh
    BROADCAST Hello, everyone! This is Node 1.
    ```

3. **Discover neighbors**:
    ```sh
    DISCOVER
    ```

4. **Check the status of the node**:
    ```sh
    STATUS
    ```

5. **Stop the node**:
    ```sh
    EXIT
    ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.