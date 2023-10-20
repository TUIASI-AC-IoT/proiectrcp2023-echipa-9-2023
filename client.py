import socket

HOST = '127.0.0.1'
PORT = 1883        

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    while True:
        message = input("Enter a message to send (or 'exit' to quit): ")
        if message.lower() == 'exit':
            break
        client.send(message.encode('utf-8'))
        response = client.recv(1024)
        print(f"Received from server: {response.decode('utf-8')}")

if __name__ == "__main__":
    main()