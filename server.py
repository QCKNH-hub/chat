import socket
import threading

# 用户数据库（实际应用中应该使用数据库存储）
users = {
    'user1': '12345678',
    'user2': '87654321'
}

# 在线用户列表
online_users = {}

def handle_client(client_socket, client_address):
    print(f"[*] 接受来自 {client_address[0]}:{client_address[1]} 的连接")
    
    try:
        # 登录验证
        client_socket.send("LOGIN".encode())
        username = client_socket.recv(1024).decode()
        password = client_socket.recv(1024).decode()
        
        if username in users and users[username] == password:
            client_socket.send("LOGIN_SUCCESS".encode())
            online_users[username] = client_socket
            print(f"[+] 用户 {username} 登录成功")
            
            # 通知其他用户
            for user, sock in online_users.items():
                if user != username:
                    sock.send(f"USER_JOINED {username}".encode())
            
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                    
                # 解析消息格式: "目标用户 消息内容"
                if " " in data:
                    target_user, message = data.split(" ", 1)
                    if target_user in online_users:
                        online_users[target_user].send(f"MSG {username}: {message}".encode())
                    else:
                        client_socket.send("USER_OFFLINE".encode())
                else:
                    # 处理其他命令
                    pass
                    
        else:
            client_socket.send("LOGIN_FAILED".encode())
            client_socket.close()
            
    except Exception as e:
        print(f"[!] 与 {client_address} 的连接出错: {e}")
    finally:
        # 用户离线处理
        if username in online_users:
            del online_users[username]
            for user, sock in online_users.items():
                sock.send(f"USER_LEFT {username}".encode())
        client_socket.close()
        print(f"[*] 与 {client_address} 的连接已关闭")

def start_server(host='0.0.0.0', port=9999):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[*] 服务器启动，监听 {host}:{port}")
    
    try:
        while True:
            client_socket, client_address = server.accept()
            client_handler = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address)
            )
            client_handler.start()
    except KeyboardInterrupt:
        print("\n[*] 服务器关闭中...")
        server.close()

if __name__ == "__main__":
    start_server()
