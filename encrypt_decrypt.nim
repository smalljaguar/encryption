import std/strutils
import std/sugar
import std/sequtils 

const BASE = ord("a"[0])
let alphabet = collect(for num in BASE..BASE+25: $chr(num)).join
proc translateText(text: string, transDict: seq[(string,string)]): string =
    return multiReplace(text,transDict)

proc caesarEncrypt(text: string, shift: int): string =
    let shiftedAlpha = alphabet[shift..alphabet.high] & alphabet[0..shift]
    let alphaSeq:seq[string] = alphabet.mapIt($it)
    let transDict = zip(alphaSeq,collect(for letter in shiftedAlpha: $letter))
    return translateText(text,transDict)


proc caesarDecrypt(text: string, shift: int): string =
    return caesarEncrypt(text, -shift+26)

assert caesarEncrypt("avecaesar", 3) == "dyhfdhvdu"
assert caesarDecrypt("dyhfdhvdu", 3) == "avecaesar"

echo caesarEncrypt(readFile("holmes-gutenberg.txt"),10)