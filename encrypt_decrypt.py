from math import log
from string import ascii_lowercase
from collections import Counter
from typing import Iterable
from math import gcd, ceil
from itertools import cycle, pairwise
from functools import lru_cache
from numpy import random  # 0.2 ms
# all funcs assume text is lowercase

BASE = ord("a")


def load_text(file: str) -> str:
    """
    Utility function which loads text file for longer sequences of text
    """
    with open(f"{file}.txt", encoding="utf8") as text:
        return text.read()


def load_wordlist() -> list[str]:
    """
    Utility function which loads text file for longer sequences of text
    """
    with open("google-10000-english-no-swears.txt") as words:
        return [word.strip() for word in words.readlines() if len(word) > 3]


words = load_wordlist()

# from https://stackoverflow.com/questions/8870261/how-to-split-text-without-spaces-into-list-of-words

# Build a cost dictionary, assuming Zipf's law and cost = -math.log(probability).
words = open("google-10000-english-no-swears.txt").read().split()
wordcost = dict((k, log((i+1)*log(len(words)))) for i, k in enumerate(words))
maxword = max(len(x) for x in words)


def infer_spaces(s: str):
    """Uses dynamic programming to infer the location of spaces in a string
    without spaces."""

    # Find the best match for the i first characters, assuming cost has
    # been built for the i-1 first characters.
    # Returns a pair (match_cost, match_length).
    def best_match(i):
        candidates = enumerate(reversed(cost[max(0, i-maxword):i]))
        return min((c + wordcost.get(s[i-k-1:i], 9e999), k+1) for k, c in candidates)

    # Build the cost array.
    cost: list = [0]
    for i in range(1, len(s)+1):
        c, k = best_match(i)
        cost.append(c)

    # Backtrack to recover the minimal-cost string.
    out = []
    i = len(s)
    while i > 0:
        c, k = best_match(i)
        assert c == cost[i]
        out.append(s[i-k:i])
        i -= k

    return " ".join(reversed(out))


def most_common(text: Iterable) -> list[tuple[str, int]]:
    # TODO: use str.count to be faster?
    return Counter([char for char in text if char not in (" ", "\n")]).most_common()


def mod_inverse(a: int) -> int:
    return pow(a, -1, 26)


def coprime(a: int, b: int) -> bool:
    return gcd(a, b) == 1


def contains_words(text, wordlist) -> float:
    count = 0
    for word in wordlist:
        if text.count(word) > 0:
            print(word)
        count += text.count(word)
    # average words per char, should be >.3 for legit text?
    return count/len(text)


def is_english(text, *cribs) -> bool:
    freq_chars = most_common(text)
    freq_onegram = most_common(
        word for word in text.split(" ") if len(word) == 1)
    if cribs != ():
        if all(crib in text for crib in cribs):
            return True
    # freq_threegram = most_common(
    #     word for word in text.split(" ") if len(word) == 3) #should be the, and for first two
    if freq_chars[0][0] == "e" and freq_chars[1][0] in ("t", "a", "i", "o") and freq_onegram[0][0] in ("a", "i"):
        return True
    return False


def normalised_common_ref():
    sample = load_text("holmes-gutenberg").lower()
    # don't filter chars in order for speeeed!
    reference = Counter(sample).most_common()
    total_chars = len([char for char in sample if char in ascii_lowercase])
    normalised_ref = dict([(char, count/total_chars)
                           for (char, count) in reference if char in ascii_lowercase])
    return normalised_ref


def pair_normalised_common_ref():
    sample = load_text("holmes-gutenberg").lower()
    filter_text = [char for char in sample if char not in ("\n")]
    reference = Counter(pairwise(filter_text)).most_common()
    total_pairs = len(filter_text)-1
    normalised_ref = dict([(pair, count/total_pairs)
                           for (pair, count) in reference])
    return normalised_ref


normalised_ref = normalised_common_ref()
normalised_ref_pairwise = pair_normalised_common_ref()


# def find_cribs() -> set[str]:
#     rare_chars = list(
#         zip(*sorted(normalised_ref.items(), key=lambda x: x[1])))[0][:5]
#     cribs = set()
#     for word in words[:]:
#         for rare_char in rare_chars:
#             if rare_char in word:
#                 cribs.add(word)
#     return cribs


# cribs = find_cribs()


def mean_abs_error(text) -> float:
    """
    Real text is < 0.01?
    """
    error = 0.0

    common_text = most_common(text)
    total_chars = len(
        [char for char in text if char in ascii_lowercase])
    normalised_text = dict([(char, count/total_chars)
                            for (char, count) in common_text if char in ascii_lowercase])
    for key in normalised_text:
        error += abs(normalised_ref[key]-normalised_text[key])
    return error/len(normalised_text)


@lru_cache
def di_mean_abs_error(text, *cribs) -> float:
    """
    Real text is < 0.01?
    """
    error = 0.0
    # filter_text = [char for char in text if char not in ("\n")]
    common_text = Counter(pairwise(text))
    total_pairs = len(text)-1
    # normalised_text = dict([(pair, count)
    #                         for (pair, count) in common_text])
    normalised_text = dict(common_text)  # remove dict to save a few ms
    for key in normalised_text:
        try:
            error += abs((normalised_ref_pairwise[key]
                         * total_pairs)-normalised_text[key])
        except KeyError:
            # print("Error! missing key, key skipped")
            error += normalised_text[key]
    for crib in cribs:  # if using more than 3 cribs, prob change the error mult
        if crib in text:
            error *= 0.8  # some value that can be finetuned
    return ((error/total_pairs))


def mean_square_error(text) -> float:
    """
    Real text is < 1e-4?
    """
    error = 0.0

    common_text = most_common(text)
    total_chars = len(
        [char for char in text if char in ascii_lowercase])
    normalised_text = dict([(char, count/total_chars)
                            for (char, count) in common_text if char in ascii_lowercase])
    for key in normalised_text:
        error += (normalised_ref[key]-normalised_text[key])**2
    return error/len(normalised_text)


def index_coincidence(text: str) -> float:
    """
    For a given ciphered message, the value for the IoC allows us to filter the list of ciphering methods

    If the Index of coincidence is high (close to 0.070)
    i.e. similar to plain text, then the message has probably been crypted using
    a transposition cipher (letters were shuffled) or a monoalphabetic substitution

    If the Index of coincidence is low (close to 0.0385)
    i.e. similar to a random text, then the message has probably been crypted using a polyalphabetic cipher
    (a letter can be replaced by multiple other ones).

    The lower the coincidence count, the more alphabets have been used.
    Example: Vigenere cipher with a key of length 4 to 8 letters have an IC of about 0.045±0.05
    """
    coincidence = denominator = 0
    common_chars = Counter(text).most_common()
    denominator = len(text)
    if denominator == 0:
        return 0
    for _, freq in common_chars:
        coincidence += freq*(freq-1)
    return coincidence/(denominator*(denominator-1))


def caesar_encrypt(text: str, shift: int) -> str:

    translate_table = {ordinal: (((ordinal +
                       shift)-BASE) % 26)+BASE for ordinal in range(BASE, BASE+26)}
    return text.translate(translate_table)


def caesar_decrypt(text: str, shift: int) -> str:
    return caesar_encrypt(text, -shift)


def smart_caesar_decrypt(text: str) -> str | None:
    for shift in range(26):
        plaintext = caesar_decrypt(text, shift)
        if mean_abs_error(plaintext) < 0.025:
            return plaintext
        print(mean_abs_error(plaintext))
    return None


def rotate(box: list[str], width: int, height: int) -> list[str]:
    return [box[y][x] for x in range(width) for y in range(height)]


def box_caesar_encrypt(text: str, width: int, sep: str = "~") -> str:
    height = ceil(len(text)/width)
    box = [text[subsection:subsection+width]
           for subsection in range(0, len(text), width)]
    if (len(text) % width) != 0:
        box[-1] += (width-(len(text) % width))*sep
    return "".join(row for row in rotate(box, width, height))


def box_caesar_decrypt(text: str, width: int) -> str:
    height = ceil(len(text)/width)
    box = [[""]*width for y in range(height)]
    for id, char in enumerate(text):
        x, y = divmod(id, height)
        box[y][x] = char
    return "".join("".join(row) for row in box).replace("~", "")


def transposition(text: str, width: int, indices: list[int]) -> str | None:
    box = [text[subsection:subsection+width]
           for subsection in range(0, len(text), width)]
    height = ceil(len(text)/width)
    new_box = [[""]*width for _ in range(height)]
    for y in range(height):
        for x, id in enumerate(indices):
            new_box[y][id] = box[y][x]
    return "".join(["".join(row) for row in new_box])


def affine_encrypt(text: str, a: int, b: int) -> str:
    translate_table = {}
    for ord_digit in range(26):
        translate_table[ord_digit+BASE] = ((a*ord_digit + b) % 26) + BASE

    return text.translate(translate_table)


def affine_decrypt(text: str, a: int, b: int) -> str:
    a = mod_inverse(a)
    b = a*-b
    return affine_encrypt(text, a, b)


def brute_affine_decrypt(ciphertext: str) -> str | None:
    for a in range(1, 12):
        for b in range(26):
            if coprime(a, 26):
                plaintext = affine_decrypt(ciphertext, a, b)
                if mean_abs_error(plaintext) < 0.01:
                    return plaintext
    return None


def vignere_encrypt(text, key):
    filter_text = "".join([char for char in text if char in ascii_lowercase])
    return "".join([chr(((ord(char_1)+ord(char_2)-BASE-BASE) %
                         26) + BASE) for (char_1, char_2) in
                    zip(filter_text, cycle(key))])
    # oneliner, hell yeah!! fuck you future me!! (assumes both are lowercase, ur fault if you don't preprocess)
    # https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher#Algebraic_description


def vignere_decrypt(text, key):
    return "".join([chr(((ord(char_1)-ord(char_2)) %
                         26) + BASE) for (char_1, char_2) in zip(text, cycle(key)) if char_1 in ascii_lowercase])


def smart_vignere(text: str, keylen: int):
    """
    Ignore for now
    use https://www.cipherchallenge.org/wp-content/uploads/2020/12/Five-ways-to-crack-a-Vigenere-cipher.pdf
    """
    parts = [text[start::keylen].ljust((len(text)//keylen)+1)
             for start in range(keylen)]
    return "".join([part for item in zip(*((part) for part in parts)) for part in item])


def ultra_smart_substitution_decrypt(text: str, *cribs: str, is_deterministic: bool = False, rand_seed=64):
    # for consistency
    if is_deterministic:
        random.seed(rand_seed)
    # based on https://sci-hub.se/10.1080/0161-119591883944
    count = 0
    for char in ascii_lowercase:
        if char not in text:
            text += char  # hack to prevent trans table missing letters
            count += 1
    error = 1.0
    revert = 0
    text_freqs = most_common(char for char in text if char in ascii_lowercase)
    if count > 0:
        text = text[:-count]
    initial_guess = zip(
        (x[0] for x in normalised_common_ref()), (x[0] for x in text_freqs))
    # placeholder for something smarter
    # weights = list(1/26 for _ in range(26))
    guess = "".maketrans(dict(initial_guess))  # type: ignore
    error = di_mean_abs_error(text.translate(guess), *cribs)
    guess_keys = list(guess.keys())
    # TODO: use combos
    x = 0
    if is_deterministic:
        pass
    else:
        while True:
            x += 1
            # choose two random letters, could be weighted
            # if we want to never repeat, shuf combos, removing when used until revert
            # when we revert, recreate combos, reshuffled?
            # choice_1, choice_2 = n_combos[-1]
            # remove last 2 elements
            choice_1, choice_2 = random.choice(
                guess_keys, 2, False)
            # swap them
            guess[choice_1], guess[choice_2] = guess[choice_2], guess[choice_1]
            new_error = di_mean_abs_error(text.translate(guess), *cribs)
            if new_error >= error:
                revert += 1
                # undo swap
                guess[choice_1], guess[choice_2] = guess[choice_2], guess[choice_1]
            else:
                error = new_error
                revert = 0
                # n_combos = combos.copy()
            if revert > 10000:  # tune this for speed against accuracy
                print("cycles = ", x, "\n error = ", error, "\n", guess)
                return text.translate(guess)


def test():
    assert ("hello there" == (caesar_decrypt(
        caesar_encrypt("hello there", 6), 6)))
    assert ("helloOO there" == affine_decrypt(
        affine_encrypt("helloOO there", 3, 7), 3, 7))
    assert (box_caesar_encrypt("AVECAESAR", 3) == "ACSVAAEER")
    assert (box_caesar_encrypt("AVECAESAR", 4) == "AARVE~ES~CA~")
    assert (box_caesar_decrypt("ACSVAAEER", 3) == "AVECAESAR")
    assert (box_caesar_decrypt("AARVE~ES~CA~", 4) == "AVECAESAR")
    assert (vignere_decrypt(vignere_encrypt(
        "attackatdawn", "lemon"), "lemon") == "attackatdawn")


def multi():
    from multiprocessing import Pool
    text = ""
    with Pool(8) as p:
        p.map(ultra_smart_substitution_decrypt, (text, "jade"))


def main():
    text = load_text(
        "ciphertexts/challenge-4-b").lower().replace("\n", " ").replace(" ", "")
    decrypt = ultra_smart_substitution_decrypt(text, "unable")
    if decrypt is None:
        raise TypeError
    print(infer_spaces(decrypt), mean_abs_error(decrypt))
    # for crib in cribs:
    #     if crib in decrypt:
    #         print(crib)

    # ciphertext = load_text("ciphertext").lower()
    # print(brute_affine_decrypt(ciphertext))


test()
if __name__ == "__main__":
    main()
