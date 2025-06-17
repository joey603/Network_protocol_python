import socket
import struct
import threading
import uuid

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

    while True:
        message = input()
        if message:
            receiver_name = message.split(' ', 1)[0]
            message_content = message.split(' ', 1)[1]
            message_id = str(uuid.uuid4())
            full_message = f"{message_id}\0{username}\0{receiver_name}\0{message_content}"
            msg = struct.pack('!BBHH', 3, 0, len(full_message.encode('utf-8')), 0) + full_message.encode('utf-8')
            client_socket.sendall(msg)
            print(f"Sent message:  {full_message}")

if __name__ == "__main__":
    main()
