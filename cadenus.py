from math import log
import random
from encrypt_decrypt import nwise
from encrypt_decrypt import pair_normalised_common_ref
from collections import Counter


def rotate(text, offset):
    return text[-offset:]+text[:-offset]

# factors are [2, 5, 10, 13, 25, 26, 50, 65, 125, 130, 250, 325, 650, 1625] for our text
# keylen probably 13
# blocksizes must be in [2, 5, 10, 13, 25, 26, 50, 65, 125, 130, 250, 325] probably > 10 maybe > 25, def != 25
# blocksize * keylen must be factor of 3250
# so say keylen 13 and blocksize 50, 13*50 = 650, in list so valid


def cadenus_encrypt(plaintext: str, key: str):
    # The Cadenus cipher involves both a columnar transposition and a rotation of the columns. The key is
    # expressed as a keyword in which repeated letters are dropped

    # 1. Divide the plaintext into blocks that are 25 times the length of the keyword (after dropping
    # repeated letters in the key).
    ciphertext = ""
    offsets = []
    for char in list(Counter(key).keys()):
        offsets.append(21) if char == "w" else offsets.append(  # skipped letter is entirely arbitrary
            "abcdefghijklmnopqrstuvxyz".index(char))

    # doesn't have to be 25, has to be in [2, 5, 10, 13, 25, 26, 50, 65, 125, 130, 250, 325, 650, 1625]
    blocksize = len(offsets)*25

    blocks = [plaintext[i:i+blocksize]
              for i in range(0, len(plaintext), blocksize)]
    # 2. For each block:
    for block in blocks:
        # a. Write the block into a matrix as though for a columnar transposition. Each column has a
        # corresponding letter from the key. Each column has 25 letters.
        width = len(offsets)  # =len(block)//25
        matrix = [block[i:i+width] for i in range(0, len(block), width)]

        columns = [x for x in zip(*matrix)]
        assert all(len(column) == 25 for column in columns)

        # b. For each column, roll it downwards by an amount determined by its letter in the key. Use
        # ‘A’ = 0, ‘B’ = 1, ..., ‘V’ = ‘W’ = 21, ..., ‘Z’ = 24 (‘V’ and ‘W’ take the same value so that
        # there are only 25 values).
        new_columns = []
        for offset, column in zip(offsets, columns):
            new_columns.append(rotate(column, offset))
    # c. Apply a columnar transposition using the keyword, without repeated letters.
        sorted_columns = [x[1] for x in sorted(
            zip(key, new_columns), key=lambda x: x[0])]
    # d. Read off this block’s part of the ciphertext by rows.

        ciphertext += "".join([item for x in zip(*sorted_columns)
                              for item in x])
    return ciphertext


def cadenus_decrypt(ciphertext, key):
    offsets = []
    for char in list(Counter(key).keys()):
        offsets.append(21) if char == "w" else offsets.append(
            "abcdefghijklmnopqrstuvxyz".index(char))
    plaintext = ""
    unsorter = [offsets.index(num) for num in sorted(offsets)]
    blocksize = len(offsets)*25
    blocks = [ciphertext[i:i+blocksize]
              for i in range(0, len(ciphertext), blocksize)]
    for block in blocks:
        rows = [block[i:i+5] for i in range(0, len(block), 5)]

        columns = ["".join(x) for x in zip(*rows)]
        sorted_columns = [x[1]
                          for x in sorted(zip(unsorter, columns), key=lambda x:x[0])]
        new_columns = []
        for offset, column in zip(offsets, sorted_columns):
            new_columns.append(rotate(column, -offset))

        plaintext += "".join([item for x in zip(*new_columns) for item in x])
    return plaintext


pair_ref = pair_normalised_common_ref(4)


def fitness(text):
    """
    Real english around or below -2?
    """
    textcount = {key: count/(len(text)*4)
                 for key, count in Counter(nwise(text.lower(), n=4)).items()}
    error = 0
    for key in pair_ref:
        if key in textcount:
            error += log(pair_ref[key])*textcount[key]
    return -error


def decipher(ciphertext, offsets, perm, keylen, block_mult=25):
    # TODO
    plaintext = ""
    unsorter = perm
    blocksize = len(offsets)*block_mult
    blocks = [ciphertext[i:i+blocksize]
              for i in range(0, len(ciphertext), blocksize)]
    for block in blocks:
        rows = [block[i:i+keylen] for i in range(0, len(block), keylen)]

        columns = ["".join(x) for x in zip(*rows)]
        sorted_columns = [x[1]
                          for x in sorted(zip(unsorter, columns), key=lambda x:x[0])]
        new_columns = []
        for offset, column in zip(offsets, sorted_columns):
            new_columns.append(rotate(column, -offset))

        plaintext += "".join([item for x in zip(*new_columns) for item in x])
    return plaintext


def hill_climb(ciphertext, keylen=5, blocksize=25):
    # attack rolling and columnar transposition separately
    # blatantly stolen from https://www.cipherchallenge.org/wp-content/uploads/2022/09/A-Book-on-Classical-Cryptography-by-Madness.pdf # noqa: E501
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVXYZ"
    parent_shifts = [0 for _ in range(keylen)]
    parent_perms = [x for x in range(keylen)]
    best_fitness = fitness(ciphertext)
    count = 0
    cutoff = 1.8
    while count < 100_000:
        child_shifts = parent_shifts
        child_perms = parent_perms
        choice = random.choice([0, 1, 2, 3])
        if choice == 0:
            # change one member of the child shift key to a random number in 0, ..., blocksize
            child_shifts[random.randint(
                0, keylen-1)] = random.randint(0, blocksize-1)
        elif choice == 1:
            # swap two randomly selected members of the child permutation
            a, b = random.sample(parent_perms, 2)
            child_perms[a], child_perms[b] = child_perms[b], child_perms[a]
        elif choice == 2:
            # randomly choose a number n from 1 to the key length
            # - roll both keys leftward n of steps (with rollover)
            # - subtract 1 from each of the last n members of the child shift key
            n = random.randint(1, keylen)
            child_shifts = rotate(child_shifts, n)
            child_perms = rotate(child_perms, n)
            child_shifts[-n:] = [(item-1) % 25 for item in child_shifts[-n:]]
            ...
        elif choice == 3:
            # randomly choose a number n from 1 to blocksize
            # - add n to each member of the child shift key, modulo blocksize
            n = random.randint(1, blocksize)
            child_shifts = [(x+n) % blocksize for x in child_shifts]
        # d. decipher the ciphertext with the child keys
        plaintext = decipher(ciphertext, child_shifts,
                             child_perms, keylen, blocksize)
        # e. calculate the new fitness of the new plaintext
        new_fitness = fitness(plaintext)
        # f. set the margin to be
        #   i. 0 if the new fitness exceeds the cutoff
        #   ii. the square root of the cutoff minus the new fitness, all divided by 10,
        #   if the new fitness is less than the cutoff
        margin = 0 if new_fitness > cutoff else ((cutoff-new_fitness)**0.5)/10
        # g. if (the new fitness exceeds the best fitness) or
        # ((the new fitness exceeds the best fitness minus the margin) and
        # (we roll a 1 on a 20-sided die))
        if new_fitness > best_fitness or (new_fitness > best_fitness-margin and random.randint(1, 20) == 1):
            print("success")
            # i. copy the child shift key into the parent shift key
            parent_shifts = child_shifts
            # ii. copy the child permutation into the parent permutation
            parent_perms = child_perms
            # iii. set the best fitness equal to the new fitness
            best_fitness = new_fitness
            # iv. set the counter to 0
            count = 0
            # h. increment the counter
        count += 1
    return plaintext


def cribbed_decrypt(ciphertext, crib, keylen=5, blocksize=25):
    # https://theblackchamber552383191.wordpress.com/2020/11/17/cadenus-extending-the-crib/
    cipher_grid = [ciphertext[i:i+keylen]
                   for i in range(0, len(ciphertext), keylen)]
    cipher_columns = [x for x in zip(*cipher_grid)]
    if len(crib) > keylen:
        for _ in range(len(crib)):
            crib = rotate(crib, 1)
            crib_grid = [crib[i:i+keylen] for i in range(0, len(crib), keylen)]
            crib_columns = [x for x in zip(*crib_grid)]
            for crib_column, cipher_column in zip(crib_columns, cipher_columns):
                if "".join(crib_column) in "".join(cipher_column):
                    print("hit!", crib_column, crib, "".join(
                        cipher_column).find("".join(crib_column)))


encrypted = cadenus_encrypt("""TO BE OR NOT TO BE THAT IS THE QUESTION WHETHER TIS NOBLER
    IN THE MIND TO SUFFER THE SLINGS AND ARROWS OF OUTRAGEOUS
    FORTUNE OR TO TAKE ARMS AGAINST A SEA OF TROUBLES AND BY
    OPPOSING END THEM TO DIE TO SLEEP NO MORE AND BY A SLEEP TO
    SAY WE END THE HEARTACHE AND THE THOUSAND NATURAL SHOCKS
    THAT FLESH IS HEIR TO TIS A CONSUMMATION DEVOUTLY TO BE
    WISHD TO DIE TO SLEEP TO SLEEP PERCHANCE TO DREAM AY THERES
    THE RUB FOR IN THAT SLEEP OF DEATH WHAT DREAMS MAY COME
    WUTEVUH""".replace(" ", "").replace("\n", ""), "oratio")

cribbed_decrypt(encrypted.lower(), "perchancetodream")

assert (cadenus_decrypt(encrypted, "oratio") == "TOBEORNOTTOBETHATISTHEQUESTIONWHETHERTISNOBLERINTHEMINDTOSUFFERTHESLINGSANDARROWSOFOUTRAGEOUSFORTUNEORTOTAKEARMSAGAINSTASEAOFTROUBLESANDBYOPPOSINGENDTHEMTODIETOSLEEPNOMOREANDBYASLEEPTOSAYWEENDTHEHEARTACHEANDTHETHOUSANDNATURALSHOCKSTHATFLESHISHEIRTOTISACONSUMMATIONDEVOUTLYTOBEWISHDTODIETOSLEEPTOSLEEPPERCHANCETODREAMAYTHERESTHERUBFORINTHATSLEEPOFDEATHWHATDREAMSMAYCOMEWUTEVUH")  # noqa: E501

# print(hill_climb(encrypted))

# print(cadenus_decrypt(open("final.txt").read().replace(" ", ""), word))
