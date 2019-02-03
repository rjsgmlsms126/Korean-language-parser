#  tools/qizvoc.py  - quizleet vocaliztion accessor
#
#
__author__ = 'jwainwright'
import http.client, urllib.parse
import base64, os, re

path = "/tts/ko.mp3?v=12&b={0}&s={1}&speed=83"
qizCookie = '''search_hit_exit=; __cf_bm=e6456829775373659a8929b47f3770b05718b8ee-1549171530-1800-AaL5vAxkRQRCOx5BoLJeSypOu+NoMquUywr3Asxafo0x1/5QGydiGYONbPOHk4CRAQzZq+1tioVfL0yWEtEAD28=; app_session_id=331c2127-70e5-4123-943a-9b49b61bfb3d; qlts=KtooeHaiTnrI3B-9YvQeWJX5E7CWqQSLOkjaSs5ym2E; _ga=GA1.2.2022167232.1535896457; _gid=GA1.2.1472799145.1549169065; akv=%7B%7D; qtkn=A8XF5UrUfbS7XFRytxwupr; _delighted_fst=1543338346535:{}; __qca=P0-1519731396-1535429426012; __cfduid=d92ab641afff733f9a0bbbf21a98e6c291535429424; fs=pe5kxc; qi5=1pr0a00fo7mxn%3A.ImjI0.HsYYLB-1YUvu.search_hit_exit=; __cf_bm=e6456829775373659a8929b47f3770b05718b8ee-1549171530-1800-AaL5vAxkRQRCOx5BoLJeSypOu+NoMquUywr3Asxafo0x1/5QGydiGYONbPOHk4CRAQzZq+1tioVfL0yWEtEAD28=; app_session_id=331c2127-70e5-4123-943a-9b49b61bfb3d; qlts=KtooeHaiTnrI3B-9YvQeWJX5E7CWqQSLOkjaSs5ym2E; _ga=GA1.2.2022167232.1535896457; _gid=GA1.2.1472799145.1549169065; akv=%7B%7D; qtkn=A8XF5UrUfbS7XFRytxwupr; _delighted_fst=1543338346535:{}; __qca=P0-1519731396-1535429426012; __cfduid=d92ab641afff733f9a0bbbf21a98e6c291535429424; fs=pe5kxc; qi5=1pr0a00fo7mxn%3A.ImjI0.HsYYLB-1YUvu.'''

headers = { "Accept": "*/*",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            # "Cookie": qizCookie,
            # "Referer": "https://quizlet.com/338582237/lesson-9-flash-cards/",
            # "Host": "quizlet.com",
            # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15",
            "Accept-Language": "en-us",
            # "Accept-Encoding": "br, gzip, deflate",
            "Connection": "keep-alive" }

def getMP3xx(conn, phrase, dest):
    "retrives MP3 vocalizatin for given phrase"
    #
    b64Phrase = base64.b64encode(phrase.encode('utf-8')).decode('utf-8')
    conn.request("GET", path.format(b64Phrase), headers=headers)
    response = conn.getresponse()
    #
    if response.status != 200:
        failReason = response.reason
    else:
        data = response.read()
        with open(dest, "wb") as outMP3:
            outMP3.write(data)

def getVox(filePath, destDir):
    "retrieve qiz vocalizations for given Anki import file, update it with names"
    #
    conn = http.client.HTTPSConnection("quizlet.com")
    #
    with open(filePath) as inf:
        with open(os.path.join(destDir, "import_plus_vox.txt"), "w") as outf:
            for i, line in enumerate(inf):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                korean, english = line.split(';')
                mp3File = os.path.join(destDir, "vox_{0}.mp3".format(i+1))
                getMP3(conn, korean, mp3File)
                print("{0};{1};[sound:{2}]".format(korean, english, mp3File), file=outf)
    #
    conn.close()


def getMP3(conn, b64, s, mp3):
    "retrives MP3 vocalizatin for given b64 phrase"
    #
    conn.request("GET", path.format(b64, s), headers=headers)
    response = conn.getresponse()
    #
    if response.status != 200:
        failReason = response.reason
    else:
        data = response.read()
        with open(mp3, "wb") as outMP3:
            outMP3.write(data)

def getVoxFromPage(pageURL, importFile, destDir):
    ""
    page = urllib.parse.urlparse(pageURL)
    #
    conn = http.client.HTTPSConnection(page.netloc)
    conn.request("GET", page.path, headers=headers)
    response = conn.getresponse()
    #
    if response.status != 200:
        print("fail!")
        return
    #
    html = response.read().decode('utf-8')
    #
    mp3Files = {}
    for m in re.finditer(r'_wordTtsUrl":"\\/tts\\/ko\.mp3\?v=12\&b=(?P<b64>[^\&]+)\&s=(?P<s>[^\&]+)\&speed=83"', html):
        print(m.groupdict())
        b64, s = m.group('b64'), m.group('s')
        mp3 = os.path.join(destDir, b64 + '.mp3')
        mp3Files[b64] = mp3
        getMP3(conn, b64, s, mp3)

    #
    conn.close()
    #
    with open(importFile) as inf:
        with open(os.path.join(destDir, "import_plus_vox.txt"), "w") as outf:
            for i, line in enumerate(inf):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                korean, english = line.split(';')
                b64 = base64.b64encode(korean.encode('utf-8')).decode('utf-8')
                mp3File = mp3Files.get(b64)
                if mp3File:
                    print("{0};{1};[sound:{2}]".format(korean, english, mp3File), file=outf)
                else:
                    print("Missing mp3 file for ", korean, english)

# https://quizlet.com/338582237/lesson-9-flash-cards/
# _wordTtsUrl":"\/tts\/ko.mp3?v=12&b=67Cp66y47ZWY64uk&s=Fzhe-REz&speed=83"

if __name__ == "__main__":
    #
    getVoxFromPage("https://quizlet.com/338582237/lesson-9-flash-cards/",
                   "/Users/jwainwright/Dropbox/Documents/한국어/Anki/import/htsk-lesson9.txt",
                   "/Users/jwainwright/Dropbox/Documents/한국어/Anki/import/")

    # getVox("/Users/jwainwright/Dropbox/Documents/한국어/Anki/import/htsk-lesson9.txt", "/Users/jwainwright/Dropbox/Documents/한국어/Anki/import/")
