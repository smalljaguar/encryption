import std/strutils
import std/sugar
import std/sequtils
import std/tables 
import std/re

const BASE = ord("a"[0])
# let alphabetSeq = collect(for num in BASE..BASE+25: $chr(num))
let alphabet = collect(for num in BASE..BASE+25: $chr(num)).join()

func translateText(text: string, transDict: seq[(string,string)]): string =
    return multiReplace(text,transDict)

proc filterLower(text:string):string {.inline} = 
    # filter_text = regex to remove all non a-z
    let filterText = toLowerAscii(re.replace(text,re"[^a-z]",""))
    return filterText

proc indexCoincidence(text:string):float =
    let counter = toCountTable(text)
    let denom = len(text)*(len(text)+1)/26
    var iOC = 0
    for key,value in counter.pairs():
        ioc += value*(value-1)
    return float(ioc)/denom

proc caesarEncrypt(text: string, shift: int): string =
    let shiftedAlpha = alphabet[shift..alphabet.high] & alphabet[0..shift]
    let alphaSeq:seq[string] = alphabet.mapIt($it)
    let transDict = zip(alphaSeq,collect(for letter in shiftedAlpha: $letter))
    return translateText(text,transDict)


proc caesarDecrypt(text: string, shift: int): string =
    return caesarEncrypt(text, -shift+26)

func vignereEncrypt(text:string, key:string): string =
    return collect(for (char1, char2) in zip(text,cycle(key,len(text)).join): chr(((ord(char1)+ord(char2)-BASE-BASE) mod 26) + BASE)).join()

func vignereDecrypt(text:string, key:string): string =
    return collect(for (char1, char2) in zip(text,cycle(key,len(text)).join): chr((((ord(char1)-ord(char2)) + 26) mod 26) + BASE)).join()

proc analyseVignere(text:string): int = 
    # returns a guess of keylen using ioc ~1.7 as natural english
    for n in 1..text.high():
        if indexCoincidence(collect(for index in countup(0,text.high(),n): text[index]).join()) > 1.5:
            return n

func product(args:varargs[string], repetitions:int): seq[string] = 
    # # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    # # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
    # pools = [tuple(pool) for pool in args] * repeat
    let pools = map(sequtils.repeat(args.join(),repetitions),(n) => $n)
    # result = [[]]
    var res:seq[seq[string]] = @[newSeq[string]()]
    # for pool in pools:
    for pool in pools:
    #    result = [x+[y] for x in result for y in pool]
        var temp:seq[seq[string]] = @[newSeq[string]()]
        for x in res:
            for y in pool:
                temp.add(concat(x,@[$y]))
        res = temp
    # for prod in result:
    return collect(for prod in res:prod.join())
    #     yield tuple(prod)

proc bruteVignere(text:string,keylen:int):string = 
    echo keylen
    #~20s for 5 char key, ~2s for 4 char key with 800ish chars. If result looks like gibberish, caesardecrypt it
    for possibleKey in product(alphabet,keylen):
        if len(possibleKey) == keylen and indexCoincidence(vignereDecrypt(text,possibleKey)) > 1.7: #can change comparison param when necessary
            echo possibleKey, indexCoincidence(vignereDecrypt(text,possibleKey))
            return vignereDecrypt(text,possibleKey)
    echo "\nall keys exhausted"
        
proc wordlistVignere(text:string,keylen:int): string = 
    for line in lines("google-10000-english-no-swears.txt"):
        if len(line) == keylen and indexCoincidence(vignereDecrypt(text,line)) > 1.7: #can change comparison param when necessary
            echo line, indexCoincidence(vignereDecrypt(text,line))
            return vignereDecrypt(text,line)
    echo "\nall keys exhausted"

assert filterLower(r"ABCabcZZZ.><.??.\\\\////") == "abc"

assert vignereEncrypt("attackatdawn","lemon") == "lxfopvefrnhr"
assert vignereDecrypt("lxfopvefrnhr","lemon") == "attackatdawn"

assert caesarEncrypt("avecaesar", 3) == "dyhfdhvdu"
assert caesarDecrypt("dyhfdhvdu", 3) == "avecaesar"

when defined(test):
    # echo caesarEncrypt(readFile("holmes-gutenberg.txt"),10)
    echo indexCoincidence(filterLower(readFile("holmes-gutenberg.txt"))) # around 1.7
    let plaintext = filterLower(toLowerAscii(readFile("holmes-gutenberg.txt")))[0..1000]
    echo "plaintext:\n", plaintext
    let encrypted = vignereEncrypt(plaintext,"loop")
    echo wordlistVignere(encrypted,analyseVignere(encrypted))
    echo caesarDecrypt(bruteVignere(encrypted,analyseVignere(encrypted)),11)