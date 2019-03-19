#  tools/vocab.py  - vocab concordance tool - trying to gather all useful stuff on the NIKL top-6000 word list, meanings, samples, etc.
#
#
__author__ = 'jwainwright'
import http.client, urllib.parse
import base64, os, re, sys
from collections import defaultdict
import json, time
from pprint import pprint
from bs4 import BeautifulSoup

topikPOSMap = {
    "1":  "명",   # noun
    "2":  "동",   # verb
    "3":  "보",   # adverb
    "4":  "형",   # adjective
    "5":  "의",   # bound noun
    "6":  "관",   # determiner
    "7":  "고",   # proper noun
    "8":  "대",   # pronoun
    "9":  "수",   # number
    "10": "감",   # interjection
    "불": "불",  # unknown
}

# hangul & english unicode ranges
ranges = [(0, 0x036f), (0x3130, 0x318F), (0xAC00, 0xD7AF), (0x1100, 0x11FF), (0x1e00, 0x2c00), (0x2022, 0x2022)]
isHangulOrEnglish = lambda s: all(any(ord(c) >= r[0] and ord(c) <= r[1] for r in ranges) for c in s)
isHangul = lambda s: all(any(ord(c) >= r[0] and ord(c) <= r[1] for r in ranges[1:]) for c in s)

def loadNIKLList(filename):
    "load up the raw NIKL word list from .csv"
    niklWords = defaultdict(lambda: defaultdict(list))
    index = 0
    with open(filename) as infile:
        for line in infile:
            fields = line.strip().split(',')
            if len(fields) == 5 and len(fields[0]) and fields[0][0].isdigit():
                index += 1
                rank, word, pos, extras, level = fields
                word = re.sub(r'\d+$', '', word.strip())
                entry = dict(word=word, index=index, rank=int(rank), pos=pos, extras=extras, level=level)
                # list of entries for each POS for each word
                niklWords[word][pos].append(entry)
    #
    return niklWords

def loadTOPIKList(filename):
    "load a TOPIK-source tab-delimited list word & definition text file"
    #
    topikWords = defaultdict(lambda: defaultdict(list))
    index = 0
    with open(filename) as infile:
        for line in infile:
            fields = line.strip().split('\t')
            if len(fields) == 3:
                index += 1
                pos, word, definition = fields
                pos = topikPOSMap.get(pos, "불")
                entry = dict(word=word, index=index, pos=pos, topikDef=definition)
                topikWords[word][pos].append(entry)
    #
    return topikWords

def addTopikDefs(dest, src):
    "lookup definitions for the words in dest from src and merge across"
    #
    for word, psos in dest.items():
        for pos, entries in psos.items():
            if word in src and pos in src[word]:
                srcEntries = src[word][pos]
                if len(entries) > 1 or len(srcEntries) > 1:
                    pass
                    #pprint(entries, width=160)
                    #pprint(srcEntries, width=160)
                    #print("---------")
                else:
                    entries[0]['topikDef'] = srcEntries[0]['topikDef'].replace(' or ', ', ')

def getPage(url):
    "retrieve HTML at given URL"

    p = urllib.parse.urlparse(url)
    conn = http.client.HTTPSConnection(p.netloc)
    #
    headers = { "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15",
            "Accept-Language": "en-us",
            "Connection": "keep-alive" }

    conn.request("GET", urllib.parse.quote(p.path), headers=headers)
    response = conn.getresponse()
    #
    result = response.read().decode('utf-8') if response.status == 200 else None
    conn.close()
    #
    return result

from wiktionaryparser import WiktionaryParser
wiktionary = WiktionaryParser()
# include Korean parts-of-speech
for pos in ('suffix', 'particle', 'determiners', 'counters', 'morphemes', 'prefix', ):
    wiktionary.include_part_of_speech(pos)
    
def getWiktionaryDeets(filename, words):
    "get wiktionary details for each word"
    # chcek if JSON already present
    if os.path.exists(filename):
        with open(filename) as wdjson:
            return json.load(wdjson)
    # else create
    wd = {}
    for word in words:
        if word not in wd:
            print("getting ", word, len(wd))
            try:
                wd[word] = wiktionary.fetch(word, 'korean')
            except:
                print("Exception on fetch for", word)
            #time.sleep(2)
    #
    # save as JSON
    with open("/Users/jwainwright/Dropbox/Documents/한국어/www.korean.go.kr/wiktionary-deets.json", "w") as wdjson:
        json.dump(wd, wdjson)
    #
    return wd

def getCombined(filename, niklWords, wikDeets):
    "get combined details for each word"
    # chcek if JSON already present
    if os.path.exists(filename):
        with open(filename) as cdjson:
            return json.load(cdjson)
    # else create
    # gather & store as uncombined source JSON
    combinedDefs = { word: dict(nikl=niklDef, wik=wikDeets.get(word)) for word, niklDef in niklWords.items() }
    with open(filename, "w") as cdjson:
        json.dump(combinedDefs, cdjson)
    #
    return combinedDefs

def genDefList(combinedDefs)

if __name__ == "__main__":
    #
    niklWords = loadNIKLList("/Users/jwainwright/Dropbox/Documents/한국어/www.korean.go.kr/한국어 학습용 어휘 목록.csv")
    topik6KWords = loadTOPIKList("/Users/jwainwright/Dropbox/Documents/한국어/www.korean.go.kr/TOPIK6000.txt")
    #
    # initial TOPIK-list definition merge
    addTopikDefs(niklWords, topik6KWords)
    #
    # for word, psos in niklWords.items():
    #     for pos, entries in psos.items():
    #         if len(entries) == 1 and 'topikDef' not in entries[0]:
    #             print('** no def for ', word)
    #             pprint(entries)
    #
    # get wiktionary details
    wiktionaryDeets = getWiktionaryDeets("/Users/jwainwright/Dropbox/Documents/한국어/www.korean.go.kr/wiktionary-deets.json", niklWords.keys())
    #
    # get uncombined defs
    combinedDefs = getCombined("/Users/jwainwright/Dropbox/Documents/한국어/www.korean.go.kr/comnined-defs.json", niklWords, wiktionaryDeets)

    #
    print("end")
