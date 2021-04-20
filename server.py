import socket
import cv2

HostIP = '127.0.0.1'
HostPort = 5555

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HostIP, HostPort))
server_socket.listen(5)

image = input("Podaj nazwe pliku: ")

print(f"Server started, listening for connections.")

client_socket, client_address = server_socket.accept()
print(f"Connection from {client_address}, sending image...")

imgFile = open(image, 'rb')
for i in imgFile:
    client_socket.send(i)

imgFile.close()
print(f"[To {client_address}] Image sent!")
