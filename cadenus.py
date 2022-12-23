from collections import Counter


def rotate(text: str, offset):
    return text[-offset:]+text[:-offset]

# factors are [2, 5, 10, 13, 26, 65] for our text, possible keylens probably 5, maybe 10,
# as 25**n possibilities, so 95_367_431_640_625==2**46 if n=10; could be done overnight?,
# but if n=13, ~2**60 possibilities, would require 10**13 checks per second naively


def cadenus_encrypt(plaintext: str, key: str):
    # The Cadenus cipher involves both a columnar transposition and a rotation of the columns. The key is
    # expressed as a keyword in which repeated letters are dropped

    # 1. Divide the plaintext into blocks that are 25 times the length of the keyword (after dropping
    # repeated letters in the key).
    ciphertext = ""
    offsets = []
    for char in list(Counter(key).keys()):
        offsets.append(21) if char == "w" else offsets.append(
            "abcdefghijklmnopqrstuvxyz".index(char))

    blocksize = len(offsets)*25

    blocks = [plaintext[i:i+blocksize]
              for i in range(0, len(plaintext), blocksize)]
    # 2. For each block:
    for block in blocks:
        # a. Write the block into a matrix as though for a columnar transposition. Each column has a
        # corresponding letter from the key. Each column has 25 letters.
        width = len(offsets)  # =len(block)//25
        matrix = [block[i:i+width] for i in range(0, len(block), width)]

        columns = ["".join(x) for x in zip(*matrix)]
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

        ciphertext += "".join(["".join(x) for x in zip(*sorted_columns)])
    return ciphertext


def cadenus_decrypt(ciphertext, key):
    plaintext = ""
    offsets = []
    for char in list(Counter(key).keys()):
        offsets.append(21) if char == "w" else offsets.append(
            "abcdefghijklmnopqrstuvxyz".index(char))
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

        plaintext += "".join(["".join(x) for x in zip(*new_columns)])
    return plaintext


encrypted = cadenus_encrypt("""TO BE OR NOT TO BE THAT IS THE QUESTION WHETHER TIS NOBLER
IN THE MIND TO SUFFER THE SLINGS AND ARROWS OF OUTRAGEOUS
FORTUNE OR TO TAKE ARMS AGAINST A SEA OF TROUBLES AND BY
OPPOSING END THEM TO DIE TO SLEEP NO MORE AND BY A SLEEP TO
SAY WE END THE HEARTACHE AND THE THOUSAND NATURAL SHOCKS
THAT FLESH IS HEIR TO TIS A CONSUMMATION DEVOUTLY TO BE
WISHD TO DIE TO SLEEP TO SLEEP PERCHANCE TO DREAM AY THERES
THE RUB FOR IN THAT SLEEP OF DEATH WHAT DREAMS MAY COME
WUTEVUH""".replace(" ", "").replace("\n", ""), "oratio")

assert (cadenus_decrypt(encrypted, "oratio") == "TOBEORNOTTOBETHATISTHEQUESTIONWHETHERTISNOBLERINTHEMINDTOSUFFERTHESLINGSANDARROWSOFOUTRAGEOUSFORTUNEORTOTAKEARMSAGAINSTASEAOFTROUBLESANDBYOPPOSINGENDTHEMTODIETOSLEEPNOMOREANDBYASLEEPTOSAYWEENDTHEHEARTACHEANDTHETHOUSANDNATURALSHOCKSTHATFLESHISHEIRTOTISACONSUMMATIONDEVOUTLYTOBEWISHDTODIETOSLEEPTOSLEEPPERCHANCETODREAMAYTHERESTHERUBFORINTHATSLEEPOFDEATHWHATDREAMSMAYCOMEWUTEVUH")  # noqa: E501


# cadenus_encrypt(open("final.txt").read().replace(" ", ""), "wowzer")
