import socket
import threading

def receive_messages(sock, username):
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                break
                
            if data.startswith("MSG "):
                print(f"\n{data[4:]}")  # 显示接收到的消息
            elif data == "USER_JOINED":
                print(f"\n[*] 用户 {data.split()[1]} 已加入聊天")
            elif data == "USER_LEFT":
                print(f"\n[*] 用户 {data.split()[1]} 已离开聊天")
            elif data == "USER_OFFLINE":
                print("\n[*] 目标用户不在线")
                
        except:
            break

def start_client(server_host='localhost', server_port=9999):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_host, server_port))
    
    # 登录流程
    print(client.recv(1024).decode())  # 等待LOGIN指令
    username = input("用户名 (user1/user2): ")
    password = input("密码: ")
    
    client.send(username.encode())
    client.send(password.encode())
    
    response = client.recv(1024).decode()
    if response == "LOGIN_SUCCESS":
        print("[+] 登录成功!")
        
        # 启动接收消息线程
        recv_thread = threading.Thread(
            target=receive_messages,
            args=(client, username)
        )
        recv_thread.daemon = True
        recv_thread.start()
        
        # 主线程处理用户输入
        while True:
            message = input()
            if message.lower() == 'exit':
                break
            # 发送消息格式: "目标用户 消息内容"
            target_user = 'user1' if username == 'user2' else 'user2'
            client.send(f"{target_user} {message}".encode())
            
    else:
        print("[!] 登录失败，请检查用户名和密码")
        client.close()
        return
        
    client.close()

if __name__ == "__main__":
    start_client()
