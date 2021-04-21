import socket

HostIP = input("Type IP (leave blank for 127.0.0.1): ")
if not HostIP:
    HostIP = '127.0.0.1'
    
HostPort = 5555

name = input("Type file name to save: ")
file = open(name, "wb")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HostIP, HostPort))

while True:
    received = client_socket.recv(1024)
    if str(received) == "b''":
        break
    file.write(received)

print(f"File was saved.")
file.close()
client_socket.close()

