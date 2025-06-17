import socket
import threading
import struct
import uuid

# List of available ports
ports = [5001, 5002, 5003, 5004, 5005]

# Dictionary to keep track of active servers and clients
active_servers = {}
client_names = {}
received_messages = set()  # Set to track received message IDs

# Lock to synchronize access to the dictionaries
active_servers_lock = threading.Lock()
client_names_lock = threading.Lock()
received_messages_lock = threading.Lock()

def handle_client_connection(client_socket, client_address):
    try:
        while True:
            # Receive the initial 6 bytes
            initial_data = client_socket.recv(6)
            if len(initial_data) < 6:
                print("Incomplete initial data received")
                break

            # Unpack the initial data
            msg_type, msg_subtype, msg_len, msg_sublen = struct.unpack('!BBHH', initial_data)
            print(f"Received message: type={msg_type}, subtype={msg_subtype}, len={msg_len}, sublen={msg_sublen}")

            # Receive the rest of the message based on msg_len
            remaining_data = client_socket.recv(msg_len) if msg_len > 0 else b''
            if len(remaining_data) < msg_len:
                print("Incomplete remaining data received")
                break
            print(f"Received data: {remaining_data}")

            if msg_type == 0:  # Request for information
                if msg_subtype == 0:  # Information about connected servers
                    with active_servers_lock:
                        response_data = '\0'.join([f"{ip}:{port}" for port, ip in active_servers.items()]).encode('utf-8')
                elif msg_subtype == 1:  # Information about connected users
                    with client_names_lock:
                        response_data = '\0'.join(client_names.keys()).encode('utf-8')
                else:
                    response_data = b''

                response_msg = struct.pack('!BBHH', 1, msg_subtype, len(response_data), 0) + response_data
                client_socket.sendall(response_msg)
                print(f"Sent response: {response_msg}")

            elif msg_type == 1 and msg_subtype == 1:  # Announce new server
                new_server_port = int(remaining_data.decode('utf-8'))
                with active_servers_lock:
                    if new_server_port not in active_servers:
                        active_servers[new_server_port] = client_address[0]
                        print(f"Updated active servers: {active_servers}")
                        # Announce this server's presence to the new server
                        announce_to_new_server(new_server_port)

            elif msg_type == 2:  # Define user name for connection
                if msg_subtype == 1:  # For a user
                    user_name = remaining_data.decode('utf-8')
                    with client_names_lock:
                        client_names[user_name] = client_socket
                    print(f"Updated client names: {list(client_names.keys())}")

            elif msg_type == 3:  # Send message
                parts = remaining_data.split(b'\0', 3)
                if len(parts) < 4:
                    print("Message format error")
                    continue

                message_id = parts[0].decode('utf-8')
                sender_name = parts[1].decode('utf-8')
                receiver_name = parts[2].decode('utf-8')
                message_content = parts[3].decode('utf-8')
                full_message = f"{sender_name}: {message_content}"

                with received_messages_lock:
                    if message_id in received_messages:
                        print(f"Duplicate message {message_id} received, ignoring.")
                        continue
                    received_messages.add(message_id)

                print(f"Message from {sender_name} to {receiver_name}: {message_content}")

                with client_names_lock:
                    if receiver_name in client_names:
                        receiver_socket = client_names[receiver_name]
                        try:
                            receiver_socket.sendall(full_message.encode('utf-8'))
                            print(f"Sent message to local client {receiver_name}")
                        except ConnectionResetError:
                            print(f"Connection reset by {receiver_name}")
                            with client_names_lock:
                                del client_names[receiver_name]
                        except Exception as e:
                            print(f"Error sending message to {receiver_name}: {e}")
                    else:
                        # Forward the message to other servers
                        forward_message_to_servers(message_id, sender_name, receiver_name, message_content)

            elif msg_type == 4:  # Echo message
                echo_response = struct.pack('!BBHH', 4, 0, 0, 0)
                client_socket.sendall(echo_response)
                print("Sent echo response")

            elif msg_type == 5:  # Disconnect message
                user_name = remaining_data.decode('utf-8')
                with client_names_lock:
                    if user_name in client_names:
                        del client_names[user_name]
                print(f"User {user_name} disconnected")

    except ConnectionResetError:
        print("Connection was reset.")
    except Exception as e:
        print(f"Error handling client connection: {e}")
    finally:
        client_socket.close()

def server_thread(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen(5)
        print(f"Server listening on port {port}")

        with active_servers_lock:
            active_servers[port] = '127.0.0.1'

        announce_to_other_servers(port)

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")
            threading.Thread(target=handle_client_connection, args=(client_socket, client_address), daemon=True).start()
    except OSError as e:
        if e.errno == 48:
            print(f"Port {port} is already in use.")
        else:
            print(f"An error occurred: {e}")

def announce_to_other_servers(port):
    for p in ports:
        if p != port:
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect(('localhost', p))
                announce_msg = struct.pack('!BBHH', 1, 1, 4, 0) + str(port).encode('utf-8')
                client_socket.sendall(announce_msg)
                client_socket.close()
                print(f"Announced to server on port {p}")
            except ConnectionRefusedError:
                print(f"Connection to server on port {p} refused")

def announce_to_new_server(new_server_port):
    for port in active_servers.keys():
        if port != new_server_port:
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect(('localhost', new_server_port))
                announce_msg = struct.pack('!BBHH', 1, 1, 4, 0) + str(port).encode('utf-8')
                client_socket.sendall(announce_msg)
                client_socket.close()
                print(f"Announced to new server on port {new_server_port}")
            except ConnectionRefusedError:
                print(f"Connection to new server on port {new_server_port} refused")

def forward_message_to_servers(message_id, sender_name, receiver_name, message_content):
    full_message = f"{message_id}\0{sender_name}\0{receiver_name}\0{message_content}"
    for p in active_servers.keys():
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', p))
            msg = struct.pack('!BBHH', 3, 0, len(full_message.encode('utf-8')), 0) + full_message.encode('utf-8')
            client_socket.sendall(msg)
            client_socket.close()
            print(f"Forwarded message to server on port {p}")
        except ConnectionRefusedError:
            print(f"Connection to server on port {p} refused")

def display_active_servers():
    while True:
        with active_servers_lock:
            print(f"Active servers: {active_servers}")
        with client_names_lock:
            print(f"Client names: {list(client_names.keys())}")
        threading.Event().wait(5)

def main():
    print("Choose a port index from the list:")
    for i, port in enumerate(ports):
        print(f"{i}: {port}")

    while True:
        try:
            index = int(input("Enter the index of the port you want to use: "))
            if 0 <= index < len(ports):
                chosen_port = ports[index]
                break
            else:
                print("Invalid index. Please choose a valid index from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    threading.Thread(target=server_thread, args=(chosen_port,), daemon=True).start()
    threading.Thread(target=display_active_servers, daemon=True).start()

    while True:
        threading.Event().wait(1)

if __name__ == "__main__":
    main()


