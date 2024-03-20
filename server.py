import socket
import ssl
import select
import threading

def broadcast_messages(client_socket, client_message, all_clients):
    for client in all_clients:
        if client != client_socket:
            try:
                client.send(client_message)
            except Exception as e:
                print(f"Error sending message: {e}")
                client.close()
                all_clients.remove(client)

def client_thread(client_socket, all_clients):
    client_socket.send(b'Welcome to the chat room!')
    
    while True:
        try:
            message = client_socket.recv(2048)
            if message:
                print(f"Received message: {message}")
                broadcast_messages(client_socket, message, all_clients)
            else:
                client_socket.close()
                all_clients.remove(client_socket)
        except Exception as e:
            print(f"Error: {e}")
            break

def main():
    host = 'localhost'
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Wrap the socket with SSL for encryption
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # Only use TLSv1.2
    
    server_socket.bind((host, port))
    server_socket.listen(4)
    
    all_clients = []
    
    print("Server started. Waiting for connections...")
    
    while True:
        read_sockets, _, _ = select.select([server_socket] + all_clients, [], [], 0)
        
        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                
                # Wrap the client's socket with SSL
                secure_client_socket = context.wrap_socket(client_socket, server_side=True)
                
                all_clients.append(secure_client_socket)
                print(f"Connection from {client_address} has been established.")
                
                threading.Thread(target=client_thread, args=(secure_client_socket, all_clients)).start()
            else:
                client_thread(notified_socket, all_clients)
    
    server_socket.close()

if __name__ == "__main__":
    main()
