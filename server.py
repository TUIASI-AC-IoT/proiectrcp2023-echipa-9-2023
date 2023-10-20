import socket
import threading

HOST = '127.0.0.1'
PORT = 1883

# Function to handle each client
def handle_client(client_socket):
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break
        decoded_message = decode_message(message)
        print(f"Received from client: {decoded_message}")

        ack_message = encode_message("ACK: " + decoded_message)
        client_socket.send(ack_message.encode('utf-8'))
    client_socket.close()

def encode_message(message):
    """
    Return the message as is.
    """
    return message

def decode_message(message):
    """
    Return the message as is.
    """
    return message

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Server was started on {HOST}:{PORT}")

    while True:
        client_sock, address = server.accept()
        print(f"[*] Accepted connection from {address[0]}:{address[1]}")
        
        client_handler = threading.Thread(target=handle_client, args=(client_sock,))
        client_handler.start()

if __name__ == "__main__":
    main()
