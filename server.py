from operator import xor
import numpy as np
import random
import cv2

# Liczniki bitów dla poszczególnych scramblerów
counter_dvb = [0, 0]
counter_v34 = [0, 0]
counter_x16 = [0, 0]

data_counter = [0, 0]

# =============== ZEGARY =================
# Metoda zegara dla scramblerów addytywnych, sprzężenie zwrotne xora dla bitów ramki i sygnału wejściowego
def sync_clock(frame, data, bit, counter):
    if bit[1] != -1:                                     # Sprawdzanie czy używamy obu bitów, potrzebne dla niektórych scramblerów
        temp = xor(frame[bit[0]-1], frame[bit[1]-1])     # XOR dla bit[0] i bit[1],
    else:                                                # Jeśli tylko 1 bit, przypisujemy wartość temu bitowi
        temp = frame[bit[0]-1]
    frame.pop()                                          # Usuwanie ostatniego bitu z ramki
    frame.insert(0, temp)                                # Dodanie na początek wartości xor
    if temp == 1:                                        # Zliczanie 0 i 1, z operacji xor
        counter[1] += 1
    else:
        counter[0] += 1
    xor_value = xor(temp, data)                          # Sprzężenie zwrotne wartości syganłu wejściowego i xora z bitów ramki
    return xor_value                                     # Zwrócenie rezultatu


# Metoda zegara dla scramblerów multiplikatywnych, sprzężenie zwrotne xora dla bitów ramki i sygnału wejściowego
def async_clock(frame, data, bit, counter):
    if bit[1] != -1:                                   # Sprawdzanie czy używamy obu bitów, potrzebne dla niektórych scramblerów
      temp = xor(frame[bit[0]-1], frame[bit[1]-1])     # XOR dla bit[0] i bit[1],
    else:                                              # Jeśli tylko 1 bit, przypisujemy wartość temu bitowi
        temp = frame[bit[0]-1]
    frame.pop()                                         # Usuwanie ostatniego bitu z ramki
    xor_value = xor(temp, data)                         # Sprzężenie zwrotne wartości syganłu wejściowego i xora z bitów ramki
    if xor_value == 1:                                  # Zliczanie 0 i 1, z operacji xor
        counter[1] += 1
    else:
        counter[0] += 1
    frame.insert(0, xor_value)                           # Dodawanie na początek ramki xora
    return xor_value                                     # Rezultat zakodowanego sygnału


# Metoda zegara dla desramblerów multiplikatywnych
def reverse_async_clock(frame, data, bit):
    if bit[1] != -1:                                      # Sprawdzanie czy używamy obu bitów, potrzebne dla niektórych scramblerów
        temp = xor(frame[bit[0]-1], frame[bit[1]-1])      # XOR dla bit[0] i bit[1],
    else:                                                 # Jeśli tylko 1 bit, przypisujemy wartość temu bitowi
        temp = frame[bit[0]-1]
    frame.pop()                                         # Usuwanie ostatniego elementu ramki
    frame.insert(0, data)                               # Dodawanie na początek ramki bitu sygnału
    xor_value = xor(data, temp)                         # XOR dla bitu synganłu wejściowego i poprzedniego xora
    return xor_value                                    # Zwrócenie zdekodowanego sygnału

# =============== SCRAMBLERY =================
# DVB Scrambler addytywny
def scramDVB(bits):
    dataLength = len(bits)                                       # Długość sygnału wejściowego
    frameDVBS = [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0]    # Ramka  synchronizująca dla scramblera
    scramBit = [len(frameDVBS), len(frameDVBS)-1]                # Bity używane przy sprzężeniu zwrotnym - dla DVB jest to ostatni i przedostatni bit
    output_signal = []                                           # Tablica na dane wyjściowe
    for i in range(0, dataLength):                               # Iteracja po całej tablicy danych wejściowych
        clock_result = sync_clock(frameDVBS, bits[i], scramBit, counter_dvb)  # Eykonanie operacji zegara dla sclamblera addytywnego
        output_signal.append(clock_result)                                      # Fodanie wyników do tablicy danych wyjściowych
    return output_signal

# V34 Scrambler multiplikatywny
def scramV34(bits):
    dataLength = len(bits)
    frameV34 = [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1] # Ramka
    scramBits = [18, 23]                                                        # Bity używane w sprzężeniu zwrotym, dla V34 bit 18 i 23
    output_signal = []                                                          # Tablica na dane wyjściowe
    for i in range(0, dataLength):                                              # Iteracja po całej tablicy danych wejściowych
        clock_result = async_clock(frameV34, bits[i], scramBits, counter_v34)   # Wykonanie operacji zegara
        output_signal.append(clock_result)                                      # Dodanie wyników do tablicy danych wyjściowych
    return output_signal

# V34 Desrambler multiplikatywny
def descramV34(bits):
    dataLength = len(bits)
    frameV34 = [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1]  # Ramka
    scramBits = [18, 23]                                                   # Bity używane w sprzężeniu zwrotym, dla V34 bit 18 i 23
    output_signal = []                                                     # Tablica na dane wyjściowe
    for i in range(0, dataLength):
        clock_result = reverse_async_clock(frameV34, bits[i], scramBits)   # Operacja operacji dekodowania
        output_signal.append(clock_result)                                 # Dodanie wyników do tablicy danych wyjściowych
    return output_signal

#  x^16+1 Scrambler addytywny
def scramX16(bits):
    dataLength = len(bits)
    frameX16 = [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1]           # Ramka
    scramBit = [16, -1]                                                      # Bity używane w sprzężeniu zwrotym, dla x16 bit 16, -1 dla braku drugiego bitu
    output_signal = []                                                       # Tablica na dane wyjściowe
    for i in range(0, dataLength):
        clock_result = sync_clock(frameX16, bits[i], scramBit, counter_x16)  # Operacja zegara
        output_signal.append(clock_result)                                   # Dodanie wyników do tablicy danych wyjściowych
    return output_signal

# =============== FUNKCJE POMOCNICZE =================
# Zliczanie ilości bitów
def sumOfBits(bits):
    data_counter[0] = 0
    data_counter[1] = 0
    for i in range(0, len(bits)):
        if bits[i] == 0:
            data_counter[0] += 1
        else:
            data_counter[1] += 1


# Zamiana bajtow obrazu na bity
def image_to_bits(data, bits):  # data -> bajty, bits -> docelowe zapisanie bitów
    for i in range(0, len(data)):
        # Konwersja bajtu na bity
        current_byte = format(data[i], '08b')

        bit_array = []
        for j in range(0, len(current_byte)):
            bit_array.append(int(current_byte[j]))
        # Dodawanie bitow badanego bajtu do tablicy bitow
        for k in range(0, len(bit_array)):
            bits.append(bit_array[k])


# Zamiana bitów po zbyt długiej sekwencji pojedyńczego bitu
def switch_bits(bits):
    amount = 0         # Ilosc takich samych bitów z kolei (kazde jedno to 0.1% szans na pominięcie)
    isZeroNow = True   # Uzywane do zliczania ilości takich samych bitów z kolei
    index = 0          # Indeks pętli

    while index < len(bits):  # Dla kazdego bitu, j -> bit
        if (bits[index] == 0 and isZeroNow) or (bits[index] == 1 and not isZeroNow):  # Zliczanie
            if amount < 100:
                amount += 0.25
        else:
            isZeroNow = not isZeroNow
            amount = 0

        # Skipuje bit jak wylosuje się odpowiednia liczba
        rand = random.randint(1, 100)
        if rand <= amount:
            if bits[index] == 0:
                bits.pop(index)
                bits.insert(index, 1)
            else:
                bits.pop(index)
                bits.insert(index, 0)
        index += 1


def bits_to_bytes(bits, array):    # Zamiana z powrotem na bajty
    bit_holder = []
    bit_counter = 0
    data = []
    for i in range(0, len(bits)):
        bit_holder.append(bits[i])
        bit_counter += 1
        if bit_counter == 8:
            string = ''
            for j in range(0, len(bit_holder)):
                string += str(bit_holder[j])
            data.append(int(string, 2))
            bit_counter = 0
            bit_holder = []

    byte_counter = 0
    for i in range(0, len(array)):
        for j in range(0, len(array[i])):
            for k in range(0, len(array[i][j])):
                array[i][j][k] = data[byte_counter]
                byte_counter += 1


# =============== WYWOŁYWANIE PROGRAMU =================
# Wczytywanie pliku do wysłania
image_name = input("Type file name: ")
image = cv2.imread(image_name)
image_array = np.array(image)
image_data = []
for x in range(0, len(image_array)):
    for y in range(0, len(image_array[x])):
        for z in range(0, len(image_array[x][y])):
            image_data.append(image_array[x][y][z])

# Zamiana obrazka na bity
image_data_bits = []        # Bity początkowego obrazka
image_to_bits(image_data, image_data_bits)

# Zliczanie początkowych bitów i wyświetlanie
sumOfBits(image_data_bits)
print(f"Ilosc bitów po poszczególnych scramblowaniach")
print(f"[START] 0: {data_counter[0]}, 1: {data_counter[1]}")

# Kopiowanie obrazka i zamiana bitów w kopii
image_switched_bits = image_data_bits.copy()
switch_bits(image_switched_bits)

# Zamiana na bajty i zapisywanie
image_switched_array = image_array.copy()
bits_to_bytes(image_switched_bits, image_switched_array)
cv2.imwrite('switched_bits.jpg', image_switched_array)

# =============== DVB ================
# Scramblowanie
scrambled_dvb_bits = scramDVB(image_data_bits.copy())       # Scramblowanie
sumOfBits(scrambled_dvb_bits)                               # Zliczanie ilości bitów
print(f"[DVB] 0: {data_counter[0]}, 1: {data_counter[1]}")  # Wyświetlanie ilości na ekran
scrambled_dvb_array = image_array.copy()                    #
bits_to_bytes(scrambled_dvb_bits, scrambled_dvb_array)      # Konwersja bitów na bajty
cv2.imwrite('DVB_scrambled.jpg', scrambled_dvb_array)       # Zapisywanie zescramblowanego obrazka

# Zamiana bitów, descrambling
switch_bits(scrambled_dvb_bits)                             # Zamiana bitów
descrambled_dvb_bits = scramDVB(scrambled_dvb_bits)         # Descramblowanie
descrambled_dvb_array = image_array.copy()                  #
bits_to_bytes(descrambled_dvb_bits, descrambled_dvb_array)  # Zamiana bitów na bajty
cv2.imwrite('DVB_descrambled.jpg', descrambled_dvb_array)   # Zapisywanie zdescramblowanego obrazka

# =============== V34 ================
# Scramblowanie i zapisywanie
scrambled_v34_bits = scramV34(image_data_bits.copy())
sumOfBits(scrambled_v34_bits)
print(f"[V34] 0: {data_counter[0]}, 1: {data_counter[1]}")
scrambled_v34_array = image_array.copy()
bits_to_bytes(scrambled_v34_bits, scrambled_v34_array)
cv2.imwrite('V34_scrambled.jpg', scrambled_v34_array)

# Zamiana bitów, descrambling
switch_bits(scrambled_v34_bits)
descrambled_v34_bits = descramV34(scrambled_v34_bits)
descrambled_v34_array = image_array.copy()
bits_to_bytes(descrambled_v34_bits, descrambled_v34_array)
cv2.imwrite('V34_descrambled.jpg', descrambled_v34_array)

# =============== X16 ================
# Scramblowanie i zapisywanie
scrambled_x16_bits = scramX16(image_data_bits.copy())
sumOfBits(scrambled_x16_bits)
print(f"[X16] 0: {data_counter[0]}, 1: {data_counter[1]}")
scrambled_x16_array = image_array.copy()
bits_to_bytes(scrambled_x16_bits, scrambled_x16_array)
cv2.imwrite('X16_scrambled.jpg', scrambled_x16_array)

# Zamiana bitów, descrambling
switch_bits(scrambled_x16_bits)
descrambled_x16_bits = scramX16(scrambled_x16_bits)
descrambled_x16_array = image_array.copy()
bits_to_bytes(descrambled_x16_bits, descrambled_x16_array)
cv2.imwrite('X16_descrambled.jpg', descrambled_x16_array)