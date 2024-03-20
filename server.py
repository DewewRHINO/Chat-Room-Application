import socket
import ssl
import threading

def broadcast_messages(client_message, all_clients, sender_socket):
    for client_socket in all_clients:
        if client_socket is not sender_socket:
            try:
                client_socket.send(client_message)
            except Exception as e:
                print(f"Error broadcasting message: {e}")
                close_client_connection(client_socket, all_clients)

def close_client_connection(client_socket, all_clients):
    if client_socket in all_clients:
        all_clients.remove(client_socket)
    client_socket.close()

def client_thread(client_socket, all_clients):
    try:
        client_socket.send(b'Welcome to the chat room!\n')
        while True:
            message = client_socket.recv(2048)
            if message:
                print(f"Broadcasting message: {message.decode('utf-8').strip()}")
                broadcast_messages(message, all_clients, client_socket)
            else:
                raise Exception("Client disconnected")
    except Exception as e:
        print(f"Client disconnected: {e}")
    finally:
        close_client_connection(client_socket, all_clients)

def main():
    host = 'localhost'
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")
    
    server_socket.bind((host, port))
    server_socket.listen(4)
    
    all_clients = []
    
    print("Server started. Waiting for connections...")
    
    while True:
        try:
            client_socket, client_address = server_socket.accept()
            secure_client_socket = context.wrap_socket(client_socket, server_side=True)
            all_clients.append(secure_client_socket)
            print(f"Connection from {client_address} has been established.")
            threading.Thread(target=client_thread, args=(secure_client_socket, all_clients)).start()
        except Exception as e:
            print(f"Server error: {e}")

if __name__ == "__main__":
    main()
