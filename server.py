import socket
import numpy
import random

# Wczytywanie adresu IP serwera
import numpy as np

HostIP = input("Type IP (leave blank for 127.0.0.1): ")
if not HostIP:
    HostIP = '127.0.0.1'

# Port serwera f
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
Bytes = numpy.fromfile(image, dtype="uint8")
Bits = list(numpy.asarray(numpy.unpackbits(Bytes))) # Bity jako lista
print(Bytes)
#zmiana w tablicy od 500 indeksu do końca

amount = 0          # Ilosc takich samych bitów z kolei (kazde jedno to 0.1% szans na pominięcie)
isZeroNow = True    # Uzywane do zliczania ilości takich samych bitów z kolei
index = 0     # Indeks pętli, nie miałem pomysłu jak to sensownie zrobić xd
j=488
while j< len(Bits):      # Dla kazdego bitu, j -> bit
    if (Bits[j] == 0 and isZeroNow) or (Bits[j]  == 1 and not isZeroNow):    # Zliczanie
        if amount < 100:
            amount += 0.1
    else:
        isZeroNow = not isZeroNow
        amount = 0

    # Skipuje bit jak wylosuje się odpowiednia liczba
    rand = random.randint(1, 100)
    if rand <= amount:
        print(f"[Debug] Usuwanie bitu [Bit: {Bits[j]}] [Losowa: {rand}] [Procent: {amount}], [Index: {j}]")
        Bits.pop(j)     #usuwanie bitu na pozycji  j
        Bits.append(1); #dodawanie 1 na koniec
        amount = 0

# Ogolnie to problem jest z tym pomijaniem bitów bo jak pomija chociazby 1 bit to plik nie działa
# Próbowałem kilka wersji tego i testowałem i nie wiem jak to rozwiązać, moze wam się uda
    j += 1


# Pakowanie bitów z powrotem w bajty i wysyłanie
Bytes = np.packbits(Bits, axis=-1)
print(Bytes)
client_socket.send(Bytes)

# !! Tu trzeba jakiegoś ifa dać czy faktycznie plik się wysłał
print(f"[To {client_address}] File sent!")

# Zamykanie połączenia
imgFile.close()
server_socket.close()