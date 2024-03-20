import socket
import ssl
import select
import sys
import threading

def receive_messages(secure_socket):
    while True:
        try:
            message = secure_socket.recv(2048)
            if message:
                print(message.decode('utf-8'))
            else:
                print("Connection closed by the server.")
                break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def main():
    host = 'localhost'
    port = 12345

    # Create a socket for the client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Wrap the socket to secure it with SSL
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # Only use TLSv1.2

    secure_socket = context.wrap_socket(client_socket, server_hostname=host)
    try:
        secure_socket.connect((host, port))
    except Exception as e:
        print(f"Error connecting to server: {e}")
        sys.exit()

    print("Connected to the chat server. You can start sending messages.")

    # Start a thread to listen for incoming messages from the server
    threading.Thread(target=receive_messages, args=(secure_socket,)).start()

    while True:
        message = input()
        if message:
            try:
                secure_socket.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error sending message: {e}")
                secure_socket.close()
                break

if __name__ == "__main__":
    main()
