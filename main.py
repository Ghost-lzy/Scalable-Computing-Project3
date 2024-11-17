import sys
import select
from src.node import P2PNode

def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <node_id> <port> [bootstrap_ip bootstrap_port]")
        sys.exit(1)

    node_id = sys.argv[1]
    port = int(sys.argv[2])
    bootstrap_ip = sys.argv[3] if len(sys.argv) > 3 else None
    bootstrap_port = int(sys.argv[4]) if len(sys.argv) > 4 else None

    node = P2PNode(node_id, port)
    node.start(bootstrap_ip, bootstrap_port)

    print("Type 'exit' to stop the node.")
    try:
        while True:
            # 处理收到的消息
            for message in node.get_received_messages():
                print(f"Received: {message}")

            # 处理用户输入命令
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                command = input().strip()
                parts = command.split(" ", 1)
                action = parts[0].upper()
                args = parts[1] if len(parts) > 1 else None

                if action == "EXIT":
                    node.stop()
                    break
                elif action in node.commands:
                    # 确保 args 不为空并正确处理参数
                    if action == "SEND" and args:
                        try:
                            target_ip, target_port, content = args.split(" ", 2)
                            node.send_message(target_ip, int(target_port), content)
                        except ValueError:
                            print("Usage: send <target_ip> <target_port> <content>")
                    elif action == "BROADCAST" and args:
                        node.broadcast(args)
                    elif action == "DISCOVER":
                        node.handle_discover({"command": action})
                    elif action == "STATUS":
                        node.handle_status({"command": action})
                    else:
                        print(f"Invalid or incomplete command: {action}")
                else:
                    print(f"Unknown command: {action}")
    except KeyboardInterrupt:
        node.stop()

if __name__ == "__main__":
    main()
