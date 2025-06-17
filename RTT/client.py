import socket
import struct
import threading
import uuid
import time

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"Received: {message}")
            else:
                break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def measure_rtt(server_ip, server_port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))
        start_time = time.time()
        echo_msg = struct.pack('!BBHH', 4, 0, 0, 0)
        client_socket.sendall(echo_msg)
        client_socket.recv(6)
        end_time = time.time()
        rtt = end_time - start_time
        client_socket.close()
        return rtt
    except Exception as e:
        print(f"Error measuring RTT: {e}")
        return float('inf')

def main():
    server_port = int(input("Enter server port: "))
    username = input("Enter your username: ")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', server_port))
    print(f"Connected to server on port {server_port}")

    # Send username to server
    username_msg = struct.pack('!BBHH', 2, 1, len(username.encode('utf-8')), 0) + username.encode('utf-8')
    client_socket.sendall(username_msg)
    print(f"Sent username: {username}")

    # Start thread to receive messages
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    # Request server list
    request_msg = struct.pack('!BBHH', 0, 0, 0, 0)
    client_socket.sendall(request_msg)
    response = client_socket.recv(1024)
    _, _, response_len, _ = struct.unpack('!BBHH', response[:6])
    server_list = response[6:6+response_len].decode('utf-8').split('\0')
    print(f"Server list received: {server_list}")

    # Measure RTT to all servers
    rtts = {}
    for server in server_list:
        server_ip, server_port = server.split(':')
        server_port = int(server_port)
        rtt = measure_rtt(server_ip, server_port)
        rtts[server] = rtt
        print(f"Server {server}: RTT {rtt:.6f} seconds")

    # Select server with lowest RTT
    best_server = min(rtts, key=rtts.get)
    best_server_ip, best_server_port = best_server.split(':')
    best_server_port = int(best_server_port)
    print(f"Best server: {best_server} with RTT {rtts[best_server]:.6f} seconds")

    # Disconnect from current server
    disconnect_msg = struct.pack('!BBHH', 5, 0, len(username.encode('utf-8')), 0) + username.encode('utf-8')
    client_socket.sendall(disconnect_msg)
    client_socket.close()

    # Connect to best server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((best_server_ip, best_server_port))
    print(f"Connected to best server on port {best_server_port}")

    # Send username to new server
    client_socket.sendall(username_msg)
    print(f"Sent username: {username} to new server")

    # Start thread to receive messages
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    while True:
        message = input()
        if message:
            receiver_name = message.split(' ', 1)[0]
            message_content = message.split(' ', 1)[1]
            message_id = str(uuid.uuid4())
            full_message = f"{message_id}\0{username}\0{receiver_name}\0{message_content}"
            msg = struct.pack('!BBHH', 3, 0, len(full_message.encode('utf-8')), 0) + full_message.encode('utf-8')
            client_socket.sendall(msg)
            print(f"Sent message: {full_message}")

if __name__ == "__main__":
    main()


