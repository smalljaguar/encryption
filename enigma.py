# import encrypt_decrypt


class EnigmaMachine:
    """
    TODO: implement rotors, plugboard, and reflector
    plugboard is just pairwise mono-alphabetic substitutionm
    """

    class Rotor:
        """
        functionality: monosub with stepping: similar to vignere, different stepping places per rotor
        3 rotors originally in use, but then 4, with choice from 8 rotors
        right hand rotor steps forward on every char, with others moving less frequently (called turnovers)
        Turnover table
        Rotor| Turnover
             | Position
        I    | R
        II   | F
        III  | W
        IV   | K
        V    | A
        VI, VII, VIII - A and N (never gonna implement these lol)
        look here: https://en.wikipedia.org/wiki/Enigma_rotor_details#Rotor_wiring_tables for wiring tables
        remember to implement doublestep with a flag (see here: https://www.cryptomuseum.com/crypto/enigma/working.htm)
        """

        def __init__(self, rotorNum: int, startPos: int, ringSetting: int) -> None:
            if not (0 < rotorNum <= 6):
                raise IndexError
            self.rotorNum = rotorNum  # 1 to 6
            self.turnover = {1: "r", 2: "f", 3: "w",
                             4: "k", 5: "a", 6: "an"}[rotorNum]
            self.rotorkey = ("EKMFLGDQVZNTOWYHXUSPAIBRCJ",  # rotor keys
                             "AJDKSIRUXBLHWTMCQGZNPYFVOE",
                             "BDFHJLCPRTXVZNYEIWGAKMUSQO",
                             "ESOVPZJAYQUIRHXLNFTGKDCMWB",
                             "VZBRGITYUPSDNHLXAWMJQOFECK",
                             "JPGVOUMFYQBENHZRDKASXLICTW",
                             "NZJHGRCXMYSWBOUFAIVLPEKQDT",
                             "FKQHTLXOCBJSPDZRAMEWNIUYGV")
            self.invrotor = ("UWYGADFPVZBECKMTHXSLRINQOJ",  # inverse rotor keys
                             "AJPCZWRLFBDKOTYUQGENHXMIVS",
                             "TAGBPCSDQEUFVNZHYIXJWLRKOM",
                             "HZWVARTNLGUPXQCEJMBSKDYOIF",
                             "QCYLXWENFTZOSMVJUDKGIARPHB",
                             "SKXQLHCNWARVGMEBJPTYFDZUIO",
                             "QMGYVPEDRCWTIANUXFKZOSLHJB",
                             "QJINSAYDVKBFRUHMCPLEWZTGXO")
            self.reflectorkey = ("EJMZALYXVBWFCRQUONTSPIKHGD",
                                 "YRUHQSLDPXNGOKMIEBFZCWVJAT",
                                 "FVPJIAOYEDRZXWGCTKUQSBNMHL")
            self.position = startPos
            self.ringSetting = ringSetting
            self.isReversed = False

        def step(self):
            # remember doublestepping is required
            ...

        def translate(self, text: str, isReversed: bool = False):
            ...

    class Plugboard:
        def __init__(self, cableCount: int = 10, isPaired: bool = True) -> None:
            self.cableCount = cableCount  # generally 10, when paired max is 13
            self.isPaired = isPaired  # true in the vast majority of cases
            self.isReversed = False

        def translate(self, text):
            ...

        def reverse(self):
            if not self.isPaired:
                self.isReversed = not self.isReversed

    class Reflector:
        def __init__(self, rotors: list[Rotor], board: Plugboard) -> None:
            self.rotors = rotors
            self.board = board

        def translate(self, text: str):
            for rotor in reversed(self.rotors):
                text = rotor.translate(text, True)
            text = self.board.translate(text)
            return text

    def __init__(self, rotors: list[Rotor]) -> None:
        self.rotors = rotors
