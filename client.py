import socket

HOST = '127.0.0.1'  # Server IP
PORT = 6201         # Server Port

def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        print("Connected to AlphaBank server!")
        
        while True:
            data = client_socket.recv(1024).decode()
            print(data, end="")  # Show server prompt or message

            # Get input command from the user
            message = input()
            if message.lower() == "exit":
                break

            # Send the command to the server
            client_socket.sendall(message.encode())

if __name__ == "__main__":
    start_client()
