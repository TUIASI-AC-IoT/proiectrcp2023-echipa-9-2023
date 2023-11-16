import socket
import threading

HOST = '127.0.0.1'
PORT = 1883

# Dictionary to store topics, subscribers, and last messages
topics = {}

# Acknowledgment codes and messages
ACK_SUBSCRIBE = "SUBACK"
ACK_PUBLISH = "PUBACK"
ERROR_INVALID_COMMAND = "ERR_INVALID_COMMAND"

# Function to handle each client
def handle_client(client_socket, client_address):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            if message.startswith("subscribe "):
                subscribe_topic(client_socket, message)
            else:
                publish_message(client_socket, message)
        except ConnectionResetError:
            print(f"Client at {client_address[0]}:{client_address[1]} forcibly closed the connection.")
            break
    client_socket.close()

def subscribe_topic(client_socket, message):
    topic = message.split(" ")[1]
    if topic not in topics:
        topics[topic] = {'subscribers': [], 'last_message': ''}
        # Print the updated topic list when a new topic is created
        print(f"New topic created: {topic}")
        print("Current topics:", list(topics.keys()))
    topics[topic]['subscribers'].append(client_socket)

    # Print all subscriber sockets for this topic
    print(f"Subscribers for topic '{topic}':")
    for subscriber in topics[topic]['subscribers']:
        print(subscriber.getpeername())

    # Send SUBACK acknowledgment
    client_socket.send(ACK_SUBSCRIBE.encode('utf-8'))

def publish_message(client_socket, message):
    parts = message.split(" ", 1)
    if len(parts) != 2:
        # Invalid command format
        client_socket.send(ERROR_INVALID_COMMAND.encode('utf-8'))
        return

    topic, msg = parts
    if topic in topics:
        topics[topic]['last_message'] = msg
        for subscriber_socket in topics[topic]['subscribers']:
            try:
                subscriber_socket.send(msg.encode('utf-8'))
            except:
                # Handle connection issues
                subscriber_socket.close()
                topics[topic]['subscribers'].remove(subscriber_socket)

        # Send the message back to the sender if they are subscribed
        if client_socket in topics[topic]['subscribers']:
            try:
                client_socket.send(msg.encode('utf-8'))
            except:
                # Handle connection issues
                client_socket.close()
                topics[topic]['subscribers'].remove(client_socket)

        # Send PUBACK acknowledgment
        client_socket.send(ACK_PUBLISH.encode('utf-8'))
    else:
        # Send error message if the topic doesn't exist
        client_socket.send(f"ERROR: Topic '{topic}' does not exist.".encode('utf-8'))

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Server was started on {HOST}:{PORT}")

    while True:
        try:
            client_sock, address = server.accept()
            print(f"[*] Accepted connection from {address[0]}:{address[1]}")

            # Pass client address as an argument to handle_client
            client_handler = threading.Thread(target=handle_client, args=(client_sock, address))
            client_handler.start()
        except KeyboardInterrupt:
            print("\nServer is shutting down...")
            server.close()
            break

if __name__ == "__main__":
    main()
