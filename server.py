from operator import xor
import numpy as np
import random
import cv2

# Liczniki bitów dla poszczególnych scramblerów
counter_dvb = [0, 0]
counter_v34 = [0, 0]
counter_x16 = [0, 0]
data_counter = [0, 0]

counter_dvb_diffrent_bits = []
counter_v34_diffrent_bits = []
counter_x16_diffrent_bits = []
counter_data_diffrent_bits = []

counter_dvb_longest_sequence = [0, 0]
counter_v34_longest_sequence = [0, 0]
counter_x16_longest_sequence = [0, 0]
counter_data_longest_sequence = [0, 0]

switch_intensity = 1


# =============== ZEGARY =================
# Metoda zegara dla scramblerów addytywnych, sprzężenie zwrotne xora dla bitów ramki i sygnału wejściowego
def sync_clock(frame, data, bit):
    if bit[1] != -1:                                     # Sprawdzanie czy używamy obu bitów, potrzebne dla niektórych scramblerów
        temp = xor(frame[bit[0]-1], frame[bit[1]-1])     # XOR dla bit[0] i bit[1],
    else:                                                # Jeśli tylko 1 bit, przypisujemy wartość temu bitowi
        temp = frame[bit[0]-1]
    frame.pop()                                          # Usuwanie ostatniego bitu z ramki
    frame.insert(0, temp)                                # Dodanie na początek wartości xor
    xor_value = xor(temp, data)                          # Sprzężenie zwrotne wartości syganłu wejściowego i xora z bitów ramki
    return xor_value                                     # Zwrócenie rezultatu


# Metoda zegara dla scramblerów multiplikatywnych, sprzężenie zwrotne xora dla bitów ramki i sygnału wejściowego
def async_clock(frame, data, bit):
    if bit[1] != -1:                                   # Sprawdzanie czy używamy obu bitów, potrzebne dla niektórych scramblerów
      temp = xor(frame[bit[0]-1], frame[bit[1]-1])     # XOR dla bit[0] i bit[1],
    else:                                              # Jeśli tylko 1 bit, przypisujemy wartość temu bitowi
        temp = frame[bit[0]-1]
    frame.pop()                                         # Usuwanie ostatniego bitu z ramki
    xor_value = xor(temp, data)                         # Sprzężenie zwrotne wartości syganłu wejściowego i xora z bitów ramki
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
        clock_result = sync_clock(frameDVBS, bits[i], scramBit)  # Wykonanie operacji zegara dla sclamblera addytywnego
        output_signal.append(clock_result)                                      # Dodanie wyników do tablicy danych wyjściowych
    return output_signal

# V34 Scrambler multiplikatywny
def scramV34(bits):
    dataLength = len(bits)
    frameV34 = [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1] # Ramka
    scramBits = [18, 23]                                                        # Bity używane w sprzężeniu zwrotym, dla V34 bit 18 i 23
    output_signal = []                                                          # Tablica na dane wyjściowe
    for i in range(0, dataLength):                                              # Iteracja po całej tablicy danych wejściowych
        clock_result = async_clock(frameV34, bits[i], scramBits)   # Wykonanie operacji zegara
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
        clock_result = sync_clock(frameX16, bits[i], scramBit)               # Operacja zegara
        output_signal.append(clock_result)                                   # Dodanie wyników do tablicy danych wyjściowych
    return output_signal

# =============== FUNKCJE POMOCNICZE =================
# Zliczanie ilości bitów
def sumOfBits(bits, counter):
    for i in range(0, len(bits)):
        if bits[i] == 0:
            counter[0] += 1
        else:
            counter[1] += 1


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
def switch_bits(bits, switch_chance, counter, doCount):
    maxZerosAmount = 0
    maxOnesAmount = 0
    amount = 0         # Ilosc takich samych bitów z kolei
    chance = 0         # Szansa na pominięcie bitu
    isZeroNow = True   # Uzywane do zliczania ilości takich samych bitów z kolei
    index = 5          # Indeks pętli

    while index < len(bits):  # Dla kazdego bitu, index -> bit
        if (bits[index] == 0 and isZeroNow) or (bits[index] == 1 and not isZeroNow):  # Zliczanie
            amount += 1
            chance = chance + (0.0075 * switch_chance * (amount/2.0))
            if doCount:
                if isZeroNow and maxZerosAmount < amount:
                    maxZerosAmount = amount
                elif (not isZeroNow) and maxOnesAmount < amount:
                    maxOnesAmount = amount
        else:
            isZeroNow = not isZeroNow
            amount = 0
            chance = 0

        # Skipuje bit jak wylosuje się odpowiednia liczba
        rand = random.uniform(1.0, 100.0)
        if rand <= chance:
            if bits[index] == 0:
                bits.pop(index)
                bits.insert(index, 1)
            else:
                bits.pop(index)
                bits.insert(index, 0)
        index += 1
    if doCount:
        counter[0] = maxZerosAmount
        counter[1] = maxOnesAmount


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


def tests_DVB(bits, array):
    # Potrzebne do zamiany z bitów na bajty i zapisywania
    scrambled_dvb_array = array.copy()
    descrambled_dvb_array = array.copy()

    scrambled_dvb_bits = scramDVB(bits.copy())                  # Scramblowanie
    sumOfBits(scrambled_dvb_bits, counter_dvb)                  # Zliczanie ilości bitów
    bits_to_bytes(scrambled_dvb_bits, scrambled_dvb_array)      # Konwersja bitów na bajty
    cv2.imwrite('DVB_scrambled.jpg', scrambled_dvb_array)       # Zapisywanie zescramblowanego obrazka

    # Kopia zescramblowanego obrazka, potrzebne do przywracania początkowej wersji po kazdym wykonaniu pętli
    scrambled_dvb_bits_copy = scrambled_dvb_bits.copy()

    for i in range(1, 101): # 1-100
        if i == switch_intensity:                                                     # Zapisywanie obrazka z próba nr. 50 - środkowa
            switch_bits(scrambled_dvb_bits, i, counter_dvb_longest_sequence, True)  # Switchowanie bitów
            descrambled_dvb_bits = scramDVB(scrambled_dvb_bits)  # Descramblowanie
            bits_to_bytes(descrambled_dvb_bits, descrambled_dvb_array)  # Zamiana bitów na bajty
            cv2.imwrite('DVB_descrambled.jpg', descrambled_dvb_array)   # Zapisywanie zdescramblowanego obrazka
        else:
            switch_bits(scrambled_dvb_bits, i, counter_dvb_longest_sequence, False)  # Switchowanie bitów
            descrambled_dvb_bits = scramDVB(scrambled_dvb_bits)  # Descramblowanie

        count_switched_bits(descrambled_dvb_bits, counter_dvb_diffrent_bits)
        scrambled_dvb_bits = scrambled_dvb_bits_copy.copy() # Przywracanie zescramblowanego obrazka ze zmienionymi bitami do początkowego


def tests_V34(bits, array):
    # Potrzebne do zamiany z bitów na bajty i zapisywania
    scrambled_v34_array = array.copy()
    descrambled_v34_array = array.copy()

    scrambled_v34_bits = scramV34(bits.copy())                  # Scramblowanie
    sumOfBits(scrambled_v34_bits, counter_v34)                  # Zliczanie ilości bitów
    bits_to_bytes(scrambled_v34_bits, scrambled_v34_array)      # Konwersja bitów na bajty
    cv2.imwrite('V34_scrambled.jpg', scrambled_v34_array)       # Zapisywanie zescramblowanego obrazka

    # Kopia zescramblowanego obrazka, potrzebne do przywracania początkowej wersji po kazdym wykonaniu pętli
    scrambled_v34_bits_copy = scrambled_v34_bits.copy()

    for i in range(1, 101): # 1-100
        if i == switch_intensity:                                                     # Zapisywanie obrazka z próba nr. 50 - środkowa
            switch_bits(scrambled_v34_bits, i, counter_v34_longest_sequence, True)  # Switchowanie bitów
            descrambled_v34_bits = descramV34(scrambled_v34_bits)  # Descramblowanie
            bits_to_bytes(descrambled_v34_bits, descrambled_v34_array)  # Zamiana bitów na bajty
            cv2.imwrite('V34_descrambled.jpg', descrambled_v34_array)   # Zapisywanie zdescramblowanego obrazka
        else:
            switch_bits(scrambled_v34_bits, i, counter_v34_longest_sequence, False)  # Switchowanie bitów
            descrambled_v34_bits = descramV34(scrambled_v34_bits)  # Descramblowanie
        count_switched_bits(descrambled_v34_bits, counter_v34_diffrent_bits)
        scrambled_v34_bits = scrambled_v34_bits_copy.copy() # Przywracanie zescramblowanego obrazka ze zmienionymi bitami do początkowego


def tests_X16(bits, array):
    # Potrzebne do zamiany z bitów na bajty i zapisywania
    scrambled_x16_array = array.copy()
    descrambled_x16_array = array.copy()

    scrambled_x16_bits = scramX16(bits.copy())                  # Scramblowanie
    sumOfBits(scrambled_x16_bits, counter_x16)                  # Zliczanie ilości bitów
    bits_to_bytes(scrambled_x16_bits, scrambled_x16_array)      # Konwersja bitów na bajty
    cv2.imwrite('X16_scrambled.jpg', scrambled_x16_array)       # Zapisywanie zescramblowanego obrazka

    # Kopia zescramblowanego obrazka, potrzebne do przywracania początkowej wersji po kazdym wykonaniu pętli
    scrambled_x16_bits_copy = scrambled_x16_bits.copy()

    for i in range(1, 101): # 1-100
        if i == switch_intensity:                                                     # Zapisywanie obrazka z próba nr. 50 - środkowa
            switch_bits(scrambled_x16_bits, i, counter_x16_longest_sequence, True)  # Switchowanie bitów
            descrambled_x16_bits = scramX16(scrambled_x16_bits)  # Descramblowanie
            bits_to_bytes(descrambled_x16_bits, descrambled_x16_array)  # Zamiana bitów na bajty
            cv2.imwrite('X16_descrambled.jpg', descrambled_x16_array)   # Zapisywanie zdescramblowanego obrazka
        else:
            switch_bits(scrambled_x16_bits, i, counter_x16_longest_sequence, False)  # Switchowanie bitów
            descrambled_x16_bits = scramX16(scrambled_x16_bits)  # Descramblowanie
        count_switched_bits(descrambled_x16_bits, counter_x16_diffrent_bits)
        scrambled_x16_bits = scrambled_x16_bits_copy.copy() # Przywracanie zescramblowanego obrazka ze zmienionymi bitami do początkowego


def tests_start(bits, array):
    # Zliczanie bitów
    sumOfBits(bits, data_counter)

    for i in range(1, 101):  # 1-100
        # Kopiowanie obrazka i zamiana bitów w kopii
        image_switched_bits = bits.copy()
        if i == switch_intensity:
            switch_bits(image_switched_bits, i, counter_data_longest_sequence, True)
            image_switched_array = array.copy()
            bits_to_bytes(image_switched_bits, image_switched_array)
            cv2.imwrite('switched_bits.jpg', image_switched_array)
        else:
            switch_bits(image_switched_bits, i, counter_data_longest_sequence, False)
        count_switched_bits(image_switched_bits, counter_data_diffrent_bits)


def count_switched_bits(bits, counter):
    cntr = 0  # Licznik ilości zmienionych bitów
    for i in range(0, len(image_data_bits)):  # Pętla przez całą długość danych
        if image_data_bits[i] is not bits[i]:  # Jeśli bit nie jest równy...
            cntr += 1  # ... dodaj 1 do licznika
    counter.append(cntr)  # Dodawanie licznika do listy

# =============== WYWOŁYWANIE PROGRAMU =================
# Wczytywanie pliku do wysłania
image_name = input("Type file name: ")
image = cv2.imread(image_name)
image_array = np.array(image)
cv2.imwrite('start_image.jpg', image_array)
image_data = []
for x in range(0, len(image_array)):
    for y in range(0, len(image_array[x])):
        for z in range(0, len(image_array[x][y])):
            image_data.append(image_array[x][y][z])

# Zamiana obrazka na bity
image_data_bits = []        # Bity początkowego obrazka
image_to_bits(image_data, image_data_bits)

switch_intensity = int(input("Type switching intensity [1-100] (only for in-console stats and file save): "))
if switch_intensity < 1 or switch_intensity > 100:
    print(f"Value is not between 1-100! Changing it to 50.")
    switch_intensity = 50

# =============== START ================
tests_start(image_data_bits.copy(), image_array.copy())

# =============== DVB ================
tests_DVB(image_data_bits.copy(), image_array.copy())

# =============== V34 ================
tests_V34(image_data_bits.copy(), image_array.copy())

# =============== X16 ================
tests_X16(image_data_bits.copy(), image_array.copy())

# Wyświetlanie statystyk
print(f"===== START IMAGE =====")
print(f"Amount of Bits: [0: {data_counter[0]}], [1: {data_counter[1]}]")
print(f"Longest sequence of bits: [0: {counter_data_longest_sequence[0]}], [1: {counter_data_longest_sequence[1]}]")
print(f"Amount of bits switched: {counter_data_diffrent_bits[switch_intensity-1]}")

print(f"========= DVB =========")
print(f"Amount of Bits: [0: {counter_dvb[0]}], [1: {counter_dvb[1]}]")
print(f"Longest sequence of bits: [0: {counter_dvb_longest_sequence[0]}], [1: {counter_dvb_longest_sequence[1]}]")
print(f"Amount of bits switched: {counter_dvb_diffrent_bits[switch_intensity-1]}")

print(f"========= V34 =========")
print(f"Amount of Bits: [0: {counter_v34[0]}], [1: {counter_v34[1]}]")
print(f"Longest sequence of bits: [0: {counter_v34_longest_sequence[0]}], [1: {counter_v34_longest_sequence[1]}]")
print(f"Amount of bits switched: {counter_v34_diffrent_bits[switch_intensity-1]}")

print(f"========= X16 =========")
print(f"Amount of Bits: [0: {counter_x16[0]}], [1: {counter_x16[1]}]")
print(f"Longest sequence of bits: [0: {counter_x16_longest_sequence[0]}], [1: {counter_x16_longest_sequence[1]}]")
print(f"Amount of bits switched: {counter_x16_diffrent_bits[switch_intensity-1]}")
print(f"=======================")
print(f"Ilość zamienionych bitów wyświetlana dla wartości intensywności zamiany równej {switch_intensity}!")