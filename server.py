import socket
import numpy
import random
import cv2
import time
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

image_data_bits = []

#zamiana bajtow obrazu na bity
def image_to_bits(image_data):
    for i in range(0,len(image_data)):
        #konwersja bajtu na bity
        current_byte = format(image_data[i],'08b')

        bit_array = []
        for j in range(0,len(current_byte)):
            bit_array.append(int(current_byte[j]))
        #dodawanie bitow badanego bajtu do tablicy bitow
        for k in range(0,len(bit_array)):
            image_data_bits.append(bit_array[k])


# Wczytywanie pliku do wysłania
image_name = input("Type file name: ")
image = cv2.imread(image_name)
image_array = numpy.array(image)
image_data = []
for x in range(0,len(image_array)):
    for y in range(0,len(image_array[x])):
        for z in range(0,len(image_array[x][y])):
            image_data.append(image_array[x][y][z])

image_to_bits(image_data)
# for l in range(0,len(image_data_bits)):
#     print(image_data_bits[l])

# Nasłuchiwanie połączenia
print(f"Server started, listening for connection.")
client_socket, client_address = server_socket.accept()

# Wyświetlanie informacji o przychodzącym połączeniu
print(f"Connection from {client_address}, sending file...")

# Otwieranie pliku i wysyłanie
#imgFile = open(image, 'rb')

# Rozpakowywanie bajtów na bity
#Bytes = numpy.fromfile(image, dtype="uint8")
#Bits = list(numpy.asarray(numpy.unpackbits(Bytes))) # Bity jako lista
#print(Bytes)
#zmiana w tablicy od 500 indeksu do końca

amount = 0          # Ilosc takich samych bitów z kolei (kazde jedno to 0.1% szans na pominięcie)
isZeroNow = True    # Uzywane do zliczania ilości takich samych bitów z kolei
index = 0     # Indeks pętli, nie miałem pomysłu jak to sensownie zrobić xd
j=488

while j< len(image_data_bits):      # Dla kazdego bitu, j -> bit
    if (image_data_bits[j] == 0 and isZeroNow) or (image_data_bits[j]  == 1 and not isZeroNow):    # Zliczanie
        if amount < 100:
            amount += 0.1
    else:
        isZeroNow = not isZeroNow
        #zakomentowalem wedlug jego zalecen zeby nie zerowac tej szansy
        #amount = 0

    # Skipuje bit jak wylosuje się odpowiednia liczba
    rand = random.randint(1, 100)
    if rand <= amount:
        print(f"[Debug] Usuwanie bitu [Bit: {image_data_bits[j]}] [Losowa: {rand}] [Procent: {amount}], [Index: {j}]")
        image_data_bits.pop(j)     #usuwanie bitu na pozycji  j
        #image_data_bits.append(1); #dodawanie 1 na koniec
        amount = 0
 # Ogolnie to problem jest z tym pomijaniem bitów bo jak pomija chociazby 1 bit to plik nie działa
# Próbowałem kilka wersji tego i testowałem i nie wiem jak to rozwiązać, moze wam się uda
    j += 1

#zamiana z powrotem na bajty
bit_holder = []
bit_counter = 0
data_byte_counter = 0
for i in range(0,len(image_data_bits)):
    bit_holder.append(image_data_bits[i])
    bit_counter+=1
    if bit_counter == 8:
        string = ''
        for i in range (0,len(bit_holder)):
            string+=str(bit_holder[i])
        image_data[data_byte_counter] = int(string,2)
        bit_counter = 0
        data_byte_counter += 1
        bit_holder = []

byte_counter = 0
for i in range(0,len(image_array)):
    for j in range(0,len(image_array[i])):
        for z in range(0,len(image_array[i][j])):
            image_array[i][j][z] = image_data[byte_counter]
            byte_counter+=1

#zapis obrazu
cv2.imwrite('wynik.jpg',image_array)

#reszta na dole chyba do wyrzucenia

# Pakowanie bitów z powrotem w bajty i wysyłanie
Bytes = np.packbits(image_data_bits, axis=-1)
print(Bytes)
client_socket.send(Bytes)

# !! Tu trzeba jakiegoś ifa dać czy faktycznie plik się wysłał
print(f"[To {client_address}] File sent!")

# Zamykanie połączenia
#imgFile.close()
server_socket.close()