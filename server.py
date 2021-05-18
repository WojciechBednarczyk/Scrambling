from operator import xor

import numpy
import numpy as np
import random
import cv2
import time
#liczniki bitów dla poszczególnych scramblerów
counter_dvb = [0,0]
counter_v34 = [0,0]
counter_x16 = [0,0]

data_counter = [0,0]
# ================================ Zegary
# Metoda zegara dla scramblerów addytywnych, sprzężenie zwrotne xora dla bitów ramki i sygnału wejściowego
def sync_clock(frame, data, bit, counter):
    if bit[1]!=-1:                                     # Sprawdzanie czy używamy obu bitów, potrzebne dla niektórych scramblerów
        temp = xor(frame[bit[0]-1], frame[bit[1]-1])     #  XOR dla bit[0] i bit[1],
    else:                                              # jeśli tylko 1 bit, przypisujemy wartość temu bitowi
        temp = frame[bit[0]-1]
    frame.pop()                                         # usuwanie ostatniego bitu z ramki
    frame.insert(0,temp)                            # dodanie na początek wartości xor
    if temp == 1:                                  #zliczanie 0 i 1, z operacji xor
        counter[1] +=1
    else:
        counter[0]  +=1
    xor_value = xor(temp, data)                      # sprzężenie zwrotne wartości syganłu wejściowego i xora z bitów ramki
    return xor_value                                     # zwrócenie rezultatu
#Metoda zegara dla scramblerów multiplikatywnych, sprzężenie zwrotne xora dla bitów ramki i sygnału wejściowego
def async_clock(frame, data, bit, counter):
    if bit[1]!=-1:                                     # Sprawdzanie czy używamy obu bitów, potrzebne dla niektórych scramblerów
      temp = xor(frame[bit[0]-1], frame[bit[1]-1])   # XOR dla bit[0] i bit[1],
    else:                                              # jeśli tylko 1 bit, przypisujemy wartość temu bitowi
        temp = frame[bit[0]-1]
    frame.pop()                                         # usuwanie ostatniego bitu z ramki
    xor_value = xor(temp, data)                      # sprzężenie zwrotne wartości syganłu wejściowego i xora z bitów ramki
    if xor_value==1:                                     #zliczanie 0 i 1, z operacji xor
        counter[1] +=1
    else:
        counter[0] +=1
    frame.insert(0,xor_value)                             # dodawanie na początek ramki xora
    return xor_value                                     # rezultat zakodowanego sygnału

# Metoda zegara dla desramblerów multiplikatywnych
def reverse_async_clock(frame, data, bit):
    if bit[1]!=-1:                                     # Sprawdzanie czy używamy obu bitów, potrzebne dla niektórych scramblerów
        temp = xor(frame[bit[0]-1], frame[bit[1]-1]) # XOR dla bit[0] i bit[1],
    else:                                              # jeśli tylko 1 bit, przypisujemy wartość temu bitowi
        temp = frame[bit[0]-1]
    frame.pop()                                         # Usuwanie ostatniego elementu ramki
    frame.insert(0,data)                                # dodawanie na początek ramki bitu sygnału
    xor_value = xor(data, temp)                      # XOR dla bitu synganłu wejściowego i poprzedniego xora
    return xor_value                                     # Zwrócenie zdekodowanego sygnału
# ===============SCRAMBLERS================= SCRAMBLERS

# DVB Scrambler addytywny
def scramDVB(signal):
    dataLength = len(signal)                                     # Długość sygnału wejściowego
    frameDVBS=[1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0]       # Ramka  synchronizująca dla scramblera
    scramBit=[len(frameDVBS),len(frameDVBS)-1]                     # bity używane przy sprzężeniu zwrotnym - dla DVB jest to ostatni i przedostatni bit
    output_signal = []                                                  # tablica na dane wyjściowe
    for i in range(0,dataLength):                                # iteracja po całej tablicy danych wejściowych
        clock_result = sync_clock(frameDVBS,signal[i], scramBit, counter_dvb)  # wykonanie operacji zegara dla sclamblera addytywnego
        output_signal.append(clock_result)                              # dodanie wyników do tablicy danych wyjściowych
    return output_signal

# V34 Scrambler multiplikatywny
def scramV34(signal):
    dataLength = len(signal)
    frameV34 = [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1] #ramka
    scramBits = [18,23]                                          # Bity używane w sprzężeniu zwrotym, dla V34 bit 18 i 23
    output_signal = []                                                  # tablica na dane wyjściowe
    for i in range(0,dataLength):                                # iteracja po całej tablicy danych wejściowych
        clock_result = async_clock(frameV34, signal[i],scramBits, counter_v34) # wykonanie operacji zegara
        output_signal.append(clock_result)                              # dodanie wyników do tablicy danych wyjściowych
    return output_signal

# V34 Desrambler multiplikatywny
def descramV34(signal):
    dataLength = len(signal)
    frameV34 = [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1]  # ramka
    scramBits = [18, 23]                                                             # Bity używane w sprzężeniu zwrotym, dla V34 bit 18 i 23
    output_signal = []                                                                      # tablica na dane wyjściowe
    for i in range(0,dataLength):
        clock_result = reverse_async_clock(frameV34,signal[i],scramBits) # operacja operacji dekodowania
        output_signal.append(clock_result)                                       # dodanie wyników do tablicy danych wyjściowych
    return output_signal

#  x^16+1 Scrambler addytywny
def scramX16(signal):
    dataLength = len(signal)
    frameX16 = [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1] # ramka
    scramBit=[16,-1]                                              # Bity używane w sprzężeniu zwrotym, dla x16 bit 16, -1 dla braku drugiego bitu
    output_signal = []                                                   # tablica na dane wyjściowe
    for i in range(0,dataLength):
        clock_result = sync_clock(frameX16,signal[i], scramBit, counter_x16)    # operacja zegara
        output_signal.append(clock_result)                                             # dodanie wyników do tablicy danych wyjściowych
    return output_signal


def sumOfBits(signal):
    for i in range(0, len(signal)):
        if signal[i] == 0:
            data_counter[0] += 1
        else:
            data_counter[1] += 1


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














