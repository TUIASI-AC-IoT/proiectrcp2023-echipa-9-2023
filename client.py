import socket
import threading

HOST = '127.0.0.1'
PORT = 1883


def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"Received message: {message}")
        except ConnectionResetError:
            print("Connection closed by server.")
            break


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()
    print("Enter 'subscribe topic' or 'topic message' (or 'exit' to quit): ")
    while True:
        user_input = input()
        if user_input.lower() == 'exit':
            break
        client.send(user_input.encode('utf-8'))



if __name__ == "__main__":
    main()
