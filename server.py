import socket
import numpy

# Wczytywanie adresu IP serwera
HostIP = input("Type IP (leave blank for 127.0.0.1): ")
if not HostIP:
    HostIP = '127.0.0.1'

# Port serwera
HostPort = 5555

# Tworzenie serwera
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HostIP, HostPort))
server_socket.listen(5)

# Wczytywanie nazwy pliku do wysłania
image = input("Type file name: ")

# Nasłuchiwanie połączenia
print(f"Server started, listening for connection.")
client_socket, client_address = server_socket.accept()

# Wyświetlanie informacji o przychodzącym połączeniu
print(f"Connection from {client_address}, sending file...")

# Otwieranie pliku i wysyłanie
imgFile = open(image, 'rb')

# Rozpakowywanie bajtów na bity
Bytes = numpy.fromfile(image, dtype = "uint8")
Bits = numpy.unpackbits(Bytes)

amount = 0          # Ilosc takich samych bitów z kolei (kazde jedno to 1% szans na pominięcie)
isZeroNow = True    # Uzywane do zliczania ilości takich samych bitów z kolei

for j in Bits:      # Dla kazdego bitu, j -> bit
    if (j == 0 and isZeroNow) or (j == 1 and not isZeroNow):    # Zliczanie
        if amount < 100:
            amount += 1
    else:
        isZeroNow = not isZeroNow
        amount = 0
    # !! Tutaj trzeba wkleic coś zeby według procentów skipowało bit

# Pakowanie bitów z powrotem w bajty i wysyłanie
Bytes = numpy.packbits(Bits)
client_socket.send(Bytes)

# !! Tu trzeba jakiegoś ifa dać czy faktycznie plik się wysłał
print(f"[To {client_address}] File sent!")

# Zamykanie połączenia
imgFile.close()
server_socket.close()
