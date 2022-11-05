import std/strutils
import std/sugar
import std/sequtils
import std/tables 
import std/re

const BASE = ord("a"[0])
let alphabetSeq = collect(for num in BASE..BASE+25: $chr(num))
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



assert filterLower(r"ABCabcZZZ.><.??.\\\\////") == "abc"

assert vignereEncrypt("attackatdawn","lemon") == "lxfopvefrnhr"
assert vignereDecrypt("lxfopvefrnhr","lemon") == "attackatdawn"

assert caesarEncrypt("avecaesar", 3) == "dyhfdhvdu"
assert caesarDecrypt("dyhfdhvdu", 3) == "avecaesar"

when defined(test):
    echo caesarEncrypt(readFile("holmes-gutenberg.txt"),10)
    echo indexCoincidence(filterLower(readFile("holmes-gutenberg.txt"))) # around 1.7
