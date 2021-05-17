import numpy as np
import random
import cv2
import time

image_data_bits = []

# Zamiana bajtow obrazu na bity
def image_to_bits(image_data):
    for i in range(0, len(image_data)):
        # Konwersja bajtu na bity
        current_byte = format(image_data[i], '08b')

        bit_array = []
        for j in range(0, len(current_byte)):
            bit_array.append(int(current_byte[j]))
        # Dodawanie bitow badanego bajtu do tablicy bitow
        for k in range(0, len(bit_array)):
            image_data_bits.append(bit_array[k])


def switch_bits():
    amount = 0         # Ilosc takich samych bitów z kolei (kazde jedno to 0.1% szans na pominięcie)
    isZeroNow = True   # Uzywane do zliczania ilości takich samych bitów z kolei
    index = 0          # Indeks pętli

    while index < len(image_data_bits):  # Dla kazdego bitu, j -> bit
        if (image_data_bits[index] == 0 and isZeroNow) or (image_data_bits[index] == 1 and not isZeroNow):  # Zliczanie
            if amount < 100:
                amount += 0.25
        else:
            isZeroNow = not isZeroNow
            # zakomentowalem wedlug jego zalecen zeby nie zerowac tej szansy
            # ^ ale ta szansa się resetuje jak znajdzie przeciwny bit, wtedy od zera właśnie powinno liczyć szanse
            # to o czym mówił to to, zeby nie zerować po usunięciu/zamienieniu bitu, usunąłem to
            amount = 0

        # Skipuje bit jak wylosuje się odpowiednia liczba
        rand = random.randint(1, 100)
        if rand <= amount:
            print(
                f"[Debug] Zamienianie bitu [Bit: {image_data_bits[index]}] [Losowa: {rand}] [Procent: {amount}], [Index: {index}]")
            if image_data_bits[index] == 0:
                image_data_bits.pop(index)
                image_data_bits.insert(index, 1)
            else:
                image_data_bits.pop(index)
                image_data_bits.insert(index, 0)
        index += 1


def bits_to_bytes():    # Zamiana z powrotem na bajty
    bit_holder = []
    bit_counter = 0
    data_byte_counter = 0
    for i in range(0, len(image_data_bits)):
        bit_holder.append(image_data_bits[i])
        bit_counter += 1
        if bit_counter == 8:
            string = ''
            for i in range(0, len(bit_holder)):
                string += str(bit_holder[i])
            image_data[data_byte_counter] = int(string, 2)
            bit_counter = 0
            data_byte_counter += 1
            bit_holder = []

    byte_counter = 0
    for i in range(0, len(image_array)):
        for j in range(0, len(image_array[i])):
            for z in range(0, len(image_array[i][j])):
                image_array[i][j][z] = image_data[byte_counter]
                byte_counter += 1


# Wczytywanie pliku do wysłania
image_name = input("Type file name: ")
image = cv2.imread(image_name)
image_array = np.array(image)
image_data = []
for x in range(0, len(image_array)):
    for y in range(0, len(image_array[x])):
        for z in range(0, len(image_array[x][y])):
            image_data.append(image_array[x][y][z])

image_to_bits(image_data)
switch_bits()
bits_to_bytes()

#zapis obrazu
cv2.imwrite('wynik.jpg', image_array)