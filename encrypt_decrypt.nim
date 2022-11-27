#use gc:arc/orc for speeeeeeeed
#http://practicalcryptography.com/cryptanalysis/ for reference
import strutils
import sugar
import sequtils
import tables
import re
import math
import sets
import std/enumerate
import algorithm

const BASE = ord("a"[0])
# let alphabetSeq = collect(for num in BASE..BASE+25: $chr(num))
let alphabet = collect(for num in BASE..BASE+25: $chr(num)).join()

proc pairMin(x: seq[(float,int)]): (float,int) =
  ## The minimum value of `x`. `T` needs to have a `<` operator.
  var currMin = x[0][0]
  result = x[0]
  for i in 1..high(x):
    if x[i][0] < currMin: result = x[i]

proc loadTetragrams(): Table[string,float] = 
    var tetraTable: Table[string, float]
    for line in lines("english_quadgrams.txt"):
        let splitLine = line.split()
        let tetra = toLowerAscii(splitLine[0])
        let tetraCount  = parseFloat(splitline[1])
        tetraTable[tetra] = tetraCount
    return tetraTable

proc normaliseTetragrams(tetraTable:Table[string,float]):Table[string,float] = 
    let totalCount = sum(tetraTable.values().toSeq())
    var newTable = tetraTable
    for key in newTable.keys():
        newTable[key] = float(log10(float(newTable[key])/totalCount))
    return newTable

let tetraTable = normaliseTetragrams(loadTetragrams())

proc tetraScore(text:string):float =
    # should be <-6 for real text?
    var score:float = 0
    for i in 0..len(text)-(4): 
        if text[i..i+3] in tetraTable:
            score = score + tetraTable[text[i..i+3]]
        else:
            score = score + log10(1/(4*100))
    return score/float(len(text))

func translateText(text: string, transDict: seq[(string, string)]): string =
    return multiReplace(text, transDict)

proc filterLower(text: string, removeSpaces:bool = false): string {.inline.} =
    # filter_text = regex to remove all non a-z
    if removeSpaces:
        return re.replace(toLowerAscii(text),re"^[a-z]","")
    else:
        return re.replace(toLowerAscii(text), re"[^a-z ]", "")

proc indexCoincidence(text: string): float =
    let cleanText = re.replace(text,re" ","")
    let counter = toCountTable(cleanText)
    let denom = (len(cleanText)*(len(cleanText)+1))/26
    var iOC = 0
    for key, value in counter.pairs():
        ioc += value*(value-1)
    return float(ioc)/denom

proc caesarEncrypt(text: string, shift: int): string =
    if shift mod 26 == 0:
        return text
    let shiftedAlpha = alphabet[shift..alphabet.high] & alphabet[0..shift]
    let alphaSeq: seq[string] = alphabet.mapIt($it)
    let transDict = zip(alphaSeq, collect(for letter in shiftedAlpha: $letter))
    return translateText(text, transDict)

proc caesarDecrypt(text: string, shift: int): string =
    return caesarEncrypt(text, -shift+26)

proc absError(text: string): float =
    # real text is around 0.2, but can put below 0.5 to be safe?
    let sourceText = filterLower(readFile("holmes-gutenberg.txt"),true)
    let sourceCounter = toCountTable(sourceText)
    let textCounter = toCountTable(text)
    var error: float
    let totalChars = len(text)
    for key in textCounter.keys():
        error += abs(sourceCounter[key]/len(sourceText) - textCounter[
                key]/totalChars)
    return error

proc chiSquared(text: string): float =
    # real text is around 0.2, but can put below 0.5 to be safe?
    let sourceText = filterLower(readFile("holmes-gutenberg.txt"),true)
    let sourceCounter = toCountTable(sourceText)
    let textCounter = toCountTable(text)
    var error: float
    let totalChars = len(text)
    for key in textCounter.keys():
        error += ((sourceCounter[key]/len(sourceText) - textCounter[
                key]/totalChars)^2)/float(textCounter[
                key]/totalChars)
    return error

# # from https://stackoverflow.com/questions/8870261/how-to-split-text-without-spaces-into-list-of-words

# # Build a cost dictionary, assuming Zipf's law and cost = -math.log(probability).
# words = open("google-10000-english-no-swears.txt").read().split()
let words = readFile("google-10000-english-no-swears.txt").split()
# wordcost = dict((k, log((i+1)*log(len(words)))) for i, k in enumerate(words))
let wordcost = collect(for (i,k) in enumerate(words): (k, log10(float(i+1)*log10(float(len(words)))))).toTable()
# maxword = max(len(x) for x in words)
let maxword = max(map(words,word=>len(word)))
echo "maxword: ", maxword

# def infer_spaces(s: str):
proc inferSpaces(text:string):string = 
#     Uses dynamic programming to infer the location of spaces in a string
#     without spaces.
#     cost: list = [0]
    var cost = @[0.0]
#     # Find the best match for the i first characters, assuming cost has
#     # been built for the i-1 first characters.
#     # Returns a pair (match_cost, match_length).
#     def best_match(i):
    proc bestMatch(idx:int,cost:seq[float]): (float,int) = 
        let candidates = pairs(cost[max(0,idx-maxword)..min(idx,len(cost)-1)].reversed()).toSeq()
#         candidates = enumerate(reversed(cost[max(0, i-maxword):i]))
#       how to get min of pairs from first items???
        return pairMin(collect(for (k, c) in candidates: (float(c) + wordcost.getOrDefault($(text[idx-k-1..idx]), 1e20), (k+1)) ))
#         return min((c + wordcost.get(s[i-k-1:i], 9e999), k+1) for k, c in candidates)

#     # Build the cost array.
#     for i in range(1, len(s)+1):

    for i in 1..len(text):
        if i > 998:
            echo "cost ", cost
            echo "i ", i
        let (c,k) = bestMatch(i,cost)
#         c, k = best_match(i)
        cost.add(c)
#         cost.append(c)

#     # Backtrack to recover the minimal-cost string.
#     output = []
    var output: seq[string] = @[] 
#     i = len(s)
    var i = len(text)
#     while i > 0:
    while i > 0:
        let (c,k) = bestMatch(i,cost)
#         c, k = best_match(i)
        assert c == cost[i]
#         assert c == cost[i]
        output.add( $(text[i-k..i]) )
#         output.append(s[i-k:i])
        i = i-k
#         i -= k
    return join(output.reversed()," ")
#     return " ".join(reversed(out))


proc smartCaesarDecrypt(text: string): string =
    for shift in 0..25:
        let plaintext = caesarDecrypt(text, shift)
        if absError(plaintext) < 0.4:
            return plaintext
    echo "no solutions"

func vignereEncrypt(text: string, key: string): string =
    return collect(for (char1, char2) in zip(text, cycle(key, len(
            text)).join): 
                if char1==" "[0]: char1
                else: chr(((ord(char1)+ord(char2)-BASE-BASE) mod 26) +
                BASE)).join()

func vignereDecrypt(text: string, key: string): string =
    return collect(for (char1, char2) in zip(text, cycle(key, len(
            text)).join):
            if char1==" "[0]: char1
            else: chr((((ord(char1)-ord(char2)) + 26) mod 26) +
            BASE)).join()

proc monoSubEncrypt(text:string, key:string):string =
    let strAlphabet: seq[string] = alphabet.toSeq().mapIt( $it ) 
    var dedupedkey = toOrderedSet(filterLower(key).toSeq()).toSeq().mapIt( $it )
    for letter in strAlphabet:
        if not dedupedkey.contains(letter):
            dedupedkey.add(letter)
    let transTable = zip(dedupedkey,strAlphabet)
    return translateText(text,transTable)

proc monoSubDecrypt(text:string, key:string): string = 
    let strAlphabet: seq[string] = alphabet.toSeq().mapIt( $it ) 
    var dedupedkey = toOrderedSet(filterLower(key).toSeq()).toSeq().mapIt( $it )
    for letter in strAlphabet:
        if not dedupedkey.contains(letter):
            dedupedkey.add(letter)
    let transTable = zip(strAlphabet,dedupedkey)
    return translateText(text,transTable)


proc analyseVignere(text: string): int =
    # returns a guess of keylen using ioc ~1.7 as natural english
    for n in 1..text.high():
        if indexCoincidence(collect(for index in countup(0, text.high(),
                n): text[index]).join()) > 1.55:
            return n

iterator iterProduct(args: varargs[string], repetitions: int): string =
    # # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    # # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
    # shamelessly stolen from python itertools
    let pools = map(sequtils.repeat(args.join(), repetitions), (n) => $n)
    var res: seq[seq[string]] = @[newSeq[string]()]
    for count, pool in enumerate(pools):
        var temp: seq[seq[string]] = @[newSeq[string]()]
        for x in res:
            for y in pool:
                if count == (repetitions-1):
                    yield (concat(x, @[$y]).join()) 
                temp.add(concat(x, @[$y]))
        res = temp

func product(args: varargs[string], repetitions: int): seq[string] =
    # # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    # # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
    # shamelessly stolen from python itertools
    let pools = map(sequtils.repeat(args.join(), repetitions), (n) => $n)
    var res: seq[seq[string]] = @[newSeq[string]()]
    for pool in pools:
        var temp: seq[seq[string]] = @[newSeq[string]()]
        for x in res:
            for y in pool:
                temp.add(concat(x, @[$y]))
        res = temp
    return collect(for prod in res: prod.join())


proc bruteVignere(text: string, keylen: int): string =
    #TODO: add multithreading
    #~20s for 5 char key, ~2s for 4 char key , ~30s for 5char key with 800ish chars.  If result looks like gibberish, caesardecrypt it
    for possibleKey in iterProduct(alphabet, keylen-1):
        let possibleKey = "a" & possibleKey
        if len(possibleKey) == keylen and indexCoincidence(vignereDecrypt(text,
                possibleKey)) > 1.7: #can change comparison param when necessary
            return vignereDecrypt(text, possibleKey)
    echo "\nall keys exhausted"

proc smartVignere(text:string, keylen:int):string =
    var sequences: seq[string]
    var plaintext: string
    for start in 0..(keylen-1):
        sequences.add(smartCaesarDecrypt(collect(for index in countup(start,len(text)-1,keylen): text[index]).join()))
    for index in 0..len(text)-1:
        plaintext.add(sequences[index mod keylen][index div keylen])
    return plaintext

proc wordlistVignere(text: string, keylen: int): string =
    for line in lines("google-10000-english-no-swears.txt"):
        if len(line) == keylen and indexCoincidence(vignereDecrypt(text,
                line)) > 1.65: #can change comparison param when necessary
            return vignereDecrypt(text, line)
    echo "\nall keys exhausted"

assert filterLower(r"aBc.><.??.\\\\////") == "abc"

assert vignereEncrypt("attackatdawn", "lemon") == "lxfopvefrnhr"
assert vignereDecrypt("lxfopvefrnhr", "lemon") == "attackatdawn"

assert caesarEncrypt("avecaesar", 3) == "dyhfdhvdu"
assert caesarDecrypt("dyhfdhvdu", 3) == "avecaesar"


proc test() =
    let plaintext = filterLower(readFile("holmes-gutenberg.txt"),false)[0..1000]
    discard caesarEncrypt(plaintext,10)
    echo indexCoincidence(plaintext) # around 1.7
    echo tetraScore(plaintext)
    echo "plaintext:\n", plaintext[0..1000]
    let encrypted = vignereEncrypt(plaintext, "vulcans")
    assert smartVignere(encrypted,analyseVignere(encrypted)) == plaintext
    echo inferSpaces(filterLower(plaintext,true))
    assert smartCaesarDecrypt(wordlistVignere(encrypted, analyseVignere(encrypted))) == plaintext
    assert monoSubDecrypt(monoSubEncrypt("attackatdawnavecaesar","lemonbeef"),"lemonbeef") == "attackatdawnavecaesar"

when defined(test):
    test()
