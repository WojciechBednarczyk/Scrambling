import socket
import cv2

HostIP = '127.0.0.1'
HostPort = 5555

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HostIP, HostPort))

image = open('received_image.png', "wb")

while True:
    received = client_socket.recv(1024)
    if str(received) == "b''":
        break
    image.write(received)

image.close()
client_socket.close()

