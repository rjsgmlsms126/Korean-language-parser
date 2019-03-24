#  tools/vocab.py  - vocab concordance tool - trying to gather all useful stuff on the NIKL top-6000 word list, meanings, samples, etc.
#
#
__author__ = 'jwainwright'
import http.client, urllib.parse, random
import base64, os, re, sys
from collections import defaultdict
from itertools import chain
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

niklPosLabel = {
    "명":    "noun",
    "동":    "verb",
    "보":    "adverb",
    "형":    "adjective",
    "의":    "bound noun",
    "관":    "determiner",
    "고":    "proper noun",
    "대":    "pronoun",
    "수":    "number",
    "감":    "interjection",
    "불":    "unknown",
}

niklPosTags = {
    "명":    ["NNG"],
    "동":    ["VV", "VX"],
    "보":    ["MAG", "MAJ"],
    "형":    ["VA", "VCP", "VCN"],
    "의":    ["NNB"],
    "관":    ["MM"],
    "고":    ["NNP"],
    "대":    ["NP"],
    "수":    ["NR"],
    "감":    ["IC"],
    "불":    ["ZZ"],
}

# hangul & english unicode ranges
ranges = [(0, 0x036f), (0x3130, 0x318F), (0xAC00, 0xD7AF), (0x1100, 0x11FF), (0x1e00, 0x2c00), (0x2022, 0x2022)]
isHangulOrEnglish = lambda s: all(any(ord(c) >= r[0] and ord(c) <= r[1] for r in ranges) for c in s)
isHangul = lambda s: all(any(ord(c) >= r[0] and ord(c) <= r[1] for r in ranges[1:]) for c in s)

def loadNIKLList(filename):
    "load up the raw NIKL word list from .csv"
    niklWords = defaultdict(lambda: defaultdict(list))
    index = 0
    with open(os.path.expanduser(filename)) as infile:
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
    with open(os.path.expanduser(filename)) as infile:
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
                    #pass
                    pprint(entries, width=160)
                    pprint(srcEntries, width=160)
                    print("---------")
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
    filename = os.path.expanduser(filename)
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

def getTranslation(s):
    "retrieves Naver/Papago NMT translation for the given string"
    #
    try:
        failReason = translatedText = ''
        data = urllib.parse.urlencode({"source": "ko", "target": "en", "text": s, })
        headers = {"Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                   "X-Naver-Client-Id": "P3YGzu2suEI1diX0DarY",
                   "X-Naver-Client-Secret": "9yhV2ea0wC"}
        conn = http.client.HTTPSConnection("openapi.naver.com")
        conn.request("POST", "/v1/papago/n2mt", data, headers)
        response = conn.getresponse()
    except:
        # server down?
        return None, "Server not responding"
    #
    if response.status != 200:
        failReason = response.reason
    else:
        try:
            data = response.read()
            result = json.loads(data).get("message", {}).get("result")
            if result:
                translatedText = result.get('translatedText')
                if not translatedText:
                    failReason = "Naver result missing translateText"
            else:
                failReason = "Naver response missing result"
        except:
            failReason = "Ill-formed JSON response from Naver API"
    conn.close()
    #
    return translatedText, failReason

def getCombined(filename, niklWords, topik6KWords, wikDeets):
    "get combined details for each word"
    # check if JSON already present
    filename = os.path.expanduser(filename)
    if os.path.exists(filename):
        with open(filename) as cdjson:
            return json.load(cdjson)
    # else create
    # gather & store as uncombined source JSON
    lowIndex = lambda w: min(x['index'] for x in chain(*list(niklWords[w].values())))
    # build combined record
    combinedDefs = { word: dict(index=lowIndex(word), nikl=niklDef, wik=wikDeets.get(word), topik=topik6KWords.get(word)) for word, niklDef in niklWords.items() }
    # fill in any missing defs from Nave
    for word, cd in combinedDefs.items():
        if cd['topik']:
            continue
        wdef = cd['wik']
        if len(wdef) >= 1 and wdef[0].get('definitions'):
            continue
        #
        naverDef, failReason = getTranslation(word)
        print("got Naver def for ", word, naverDef)
        combinedDefs[word]['naver'] = naverDef
    #
    with open(filename, "w") as cdjson:
        json.dump(combinedDefs, cdjson, indent=2)
    #
    return combinedDefs

def genDefList(combinedDefs):
    "generate lowest-index sorted list with extracted definitions"
    index = 0
    with open(os.path.expanduser("~/Dropbox/Documents/한국어/www.korean.go.kr/fulllist.csv"), "w", encoding="utf-8") as fullList:
        with open(os.path.expanduser("~/Dropbox/Documents/한국어/www.korean.go.kr/qlist.csv"), "w", encoding="utf-8") as qList:
            for word in sorted(combinedDefs.keys(), key=lambda w: combinedDefs[w]['index']):
                cd = combinedDefs[word]
                #
                # gather topik & wiktionary defs
                topik = cd.get('topik')
                if topik:
                    tds = '; '.join("{1} ({0})".format(niklPosLabel.get(pos, '?'), ', '.join(e['topikDef'] for e in entries)) for pos, entries in topik.items())
                else:
                    tds = ''
                wkdl = []; wkdpl = []
                wik = cd.get('wik')
                if wik:
                    for wd in wik:
                        for d in wd.get('definitions',[]):
                            if d['partOfSpeech'] not in ('syllable', ):
                                entry = "{1} ({0})".format(d['partOfSpeech'], ', '.join(t for t in d['text'] if t and not isHangul(t[0])))
                                if d['partOfSpeech'] in ('suffix', 'particle'):
                                    wkdpl.append(entry)
                                else:
                                    wkdl.append(entry)
                    wds = '; '.join(wkdl)
                    wdps = '; '.join(wkdpl)
                else:
                    wds = ''
                index += 1
                # cosmetic cleanups
                def cleanup(s):
                    if s == '':
                        return s
                    s = s.strip().replace('\n', ';').replace(' (unknown)', '')
                    s = re.sub(r'(\w),(\w)', r'\1, \2', s)
                    # add To... for verbs without same
                    if word[-1] == "다" and ('verb' in s or 'adjective' in s) and not s.lower().startswith("to "):
                        s = ("To be " if 'adjective' in s else "To ") + s[0].lower() + s[1:]
                    # check for dup def phrases??
                    # ss = re.sub(r'[,;]', '', s.lower())
                    # ssw = ss.split(' ')
                    # for w in
                    dts = [w for w in s.lower().split(' ') if len(w) > 3]
                    if len(dts) != len(set(dts)):
                        print("Possible dups", index, s)
                    return s[0].capitalize() + s[1:]
                tds = cleanup(tds)
                wds = cleanup(wds)
                wdps = cleanup(wdps)
                nds = cleanup(cd.get('naver', ''))
                if len(tds + wds + nds) == 0:
                    print("*** no definition", word, index)
                # short def
                shortDef = tds or wds or nds
                cd['short'] = shortDef
                # write list csv's
                fullList.write(str(index) + '\t' + str(cd['index']) + '\t' + word + '\t' + tds + '\t' + wds + '\t' + wdps + '\t' + nds + '\n')
                qList.write(word + '\t' + shortDef + '\n')


# ------  sample sentence gatherer ------

# set up KHaiii api
import khaiii
khaiiiAPI = khaiii.KhaiiiApi()
khaiiiAPI.open()

#  first, build a word/POS concordance for the KAIST-corpora 60K sentence source
#
def genKAISTSentenceConcordance(defs, sentenceFilename):
    "generates and stores a lookup by word & POS into a reference sentence table"
    #
    # load the sentences from our morpheme-analyzed list
    index = 0
    sentences = {}  # by index
    concordance = defaultdict(set) # by morpheme:POS pair
    #
    sentenceFilename = os.path.expanduser(sentenceFilename)
    with open(sentenceFilename) as sentenceFile:
        for line in sentenceFile:
            line = line.strip()
            if line.startswith('['):
                index += 1  # bump the sentence index
                # ["How is the game?.", "시합 상황은 어떠니?", "시합:NNG;상황:NNG;은:JX;어떻:VA;니:EF"]
                english, korean, morhpemes = json.loads(line)
                sentences[index] = dict(e=english, k=korean, m=morhpemes)
                # split by morpheme
                for mp in morhpemes.split(';'):
                    # store only those for N*, V*, M*, I*, essentially the only parts-of-speech in the NIKL list
                    if mp and ';;' not in mp and '::' not in mp and mp.split(':')[1][0] in ('N', 'V', 'M', 'I'):
                        # for now, store comprehensive concordance by base:pos pair keying sentence index, even though common particles may not be needed
                        concordance[mp].add(index)
    #
    for mp, ss in concordance.items():
        concordance[mp] = list(ss)  # convert sets to lists for JSONing
    #
    # store them
    baseName = sentenceFilename.rsplit('.', 1)[0]
    with open(baseName + "-dict.json", "w") as djson:
        json.dump(sentences, djson, indent=2)
    with open(baseName + "-concordance.json", "w") as djson:
        json.dump(concordance, djson, indent=2)

    # run over combined defs, gather sample sentences for various parts of speech
    samples = defaultdict(dict)
    for word, cd in defs.items():
        niklDef = cd['nikl']
        for pos in niklDef.keys():
            for tag in niklPosTags.get(pos, ["ZZ"]):
                if tag[0] == 'V':
                    # verb, need to use Khaiii to get stem
                    key = khaiiiAPI.analyze(word)[0].morphs[0].lex.strip()
                    if key[-1] == '다':
                        # handle verbs that are also non-verbs and don't get decomposed by Khaiii (eg 보다)
                        key = key[:-1]
                else:
                    key = word
                ccs = concordance.get(key + ':' + tag)
                if ccs:
                    samples[word][niklPosLabel.get(pos, "unknown")] = ccs
                    print("====== ", word, niklPosLabel[pos], ':', cd['short'],
                          "\n  ", "\n  ".join(sentences[i]['k'] + ": " + sentences[i]['e'] for i in sorted(list(set(random.choices(ccs, k=20))), key=lambda i: len(sentences[i]['k']))[:10]))
    #
    # store samples mapping
    with open(baseName + "-samples-by-word.json", "w") as sjson:
        json.dump(samples, sjson, indent=2)


if __name__ == "__main__":
    #
    niklWords = loadNIKLList("~/Dropbox/Documents/한국어/www.korean.go.kr/한국어 학습용 어휘 목록.csv")
    topik6KWords = loadTOPIKList("~/Dropbox/Documents/한국어/www.korean.go.kr/TOPIK6000.txt")
    #
    # # initial TOPIK-list definition merge
    # addTopikDefs(niklWords, topik6KWords)
    #
    # for word, psos in niklWords.items():
    #     for pos, entries in psos.items():
    #         if len(entries) == 1 and 'topikDef' not in entries[0]:
    #             print('** no def for ', word)
    #             pprint(entries)
    #
    # get wiktionary details
    wiktionaryDeets = getWiktionaryDeets("~/Dropbox/Documents/한국어/www.korean.go.kr/wiktionary-deets.json", niklWords.keys())
    #
    # get uncombined defs
    combinedDefs = getCombined("~/Dropbox/Documents/한국어/www.korean.go.kr/combined-defs.json", niklWords, topik6KWords, wiktionaryDeets)
    #
    # generate definitions list
    genDefList(combinedDefs)
    #
    #
    genKAISTSentenceConcordance(combinedDefs, "~/Dropbox/Documents/한국어/www.korean.go.kr/kaist.corpus-60k-sentences-unicode.json")

    #
    print("end")
