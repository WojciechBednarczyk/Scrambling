import socket

# Wczytywanie docelowego adresu IP od klienta
HostIP = input("Type IP (leave blank for 127.0.0.1): ")
if not HostIP:
    HostIP = '127.0.0.1'

# Port do połączenia
HostPort = 5555

# Wczytywanie nazwy pliku, do którego chcemy zapisać odebrane dane, otwieranie pliku
name = input("Type file name to save: ")
file = open(name, "wb")

# Łączenie z serwerem
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HostIP, HostPort))

while True:
    received = client_socket.recv(1024) # Odbieranie 1024 bajtów danych od serwera
    if str(received) == "b''":          # Jeśli odebrano pusty bajt wyjdź z pętli
        break
    file.write(received)                # Zapisz odebrane dane do pliku

print(f"File was saved.")
file.close()                            # Zamykanie pliku
client_socket.close()                   # Zamykanie socketa klienta

