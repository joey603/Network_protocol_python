import socket
import threading

# List of port available
ports = [5001, 5002, 5003, 5004, 5005]

def handle_client_connection(client_socket, client_address):
    # Handle the incoming client connection
    print(f"Connection from {client_address}")
    message = client_socket.recv(1024).decode('utf-8')
    if message == 'hello':
        client_socket.sendall('world'.encode('utf-8'))
    client_socket.close()

def server_thread(port):
    # Create and configure the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Set the SO_REUSEADDR option to reuse the socket address
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen(5)
        print(f"Server listening on port {port}")

        # Accept and handle incoming connections
        while True:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_client_connection, args=(client_socket, client_address)).start()
    except OSError as e:
        if e.errno == 48:
            print(f"Port {port} is already in use.")
        else:
            print(f"An error occurred: {e}")

def try_connect_to_other_servers(port):
    # Try to connect to other servers on different ports
    for p in ports:
        if p != port:
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect(('localhost', p))
                client_socket.sendall('hello'.encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                if response == 'world':
                    print('end')
                client_socket.close()
            except ConnectionRefusedError:
                print(f"No server listening on port {p}")

def main():
    # Display the list of available ports to the user
    print("Choose a port index from the list:")
    for i, port in enumerate(ports):
        print(f"{i}: {port}")
    
    # Prompt the user to select a port
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

    # Start the server in a new thread on the chosen port
    threading.Thread(target=server_thread, args=(chosen_port,), daemon=True).start()

    # Give the server some time to start
    threading.Event().wait(1)

    # Try to connect to other servers
    try_connect_to_other_servers(chosen_port)

    # Keep the main thread running to keep the server alive
    while True:
        threading.Event().wait(1)

if __name__ == "__main__":
    main()
