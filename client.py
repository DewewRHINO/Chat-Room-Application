import socket
import ssl
import sys
import threading

def receive_messages(secure_socket):
    while True:
        try:
            message = secure_socket.recv(2048)
            if message:
                print(message.decode('utf-8'))
            else:
                raise Exception("Server closed the connection")
        except Exception as e:
            print(f"Disconnected from server: {e}")
            secure_socket.close()
            sys.exit()

def main():
    host = 'localhost'
    port = 12345
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    
    secure_socket = context.wrap_socket(client_socket, server_hostname=host)
    
    try:
        secure_socket.connect((host, port))
    except Exception as e:
        print(f"Error connecting to server: {e}")
        sys.exit()
    
    print("Connected to the chat server. You can start sending messages.")

    threading.Thread(target=receive_messages, args=(secure_socket,)).start()

    try:
        while True:
            message = input()
            if message:
                secure_socket.send(message.encode('utf-8'))
    except KeyboardInterrupt:
        print("Client exiting gracefully.")
        secure_socket.close()

if __name__ == "__main__":
    main()
