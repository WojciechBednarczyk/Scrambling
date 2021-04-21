import socket

HostIP = input("Type IP (leave blank for 127.0.0.1): ")
if not HostIP:
    HostIP = '127.0.0.1'
    
HostPort = 5555

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HostIP, HostPort))
server_socket.listen(5)

image = input("Type file name: ")

print(f"Server started, listening for connection.")

client_socket, client_address = server_socket.accept()
print(f"Connection from {client_address}, sending file...")

imgFile = open(image, 'rb')
for i in imgFile:
    client_socket.send(i)

imgFile.close()
print(f"[To {client_address}] File sent!")
