#  tools/get_samples.py  - tools to gather sample sentences for given words
#
#
__author__ = 'jwainwright'
import http.client, urllib.parse
from bs4 import BeautifulSoup

def getPage(url):
    "retrieve HTML at given URL"

    p = urllib.parse.urlparse(url)
    conn = http.client.HTTPSConnection(p.netloc)
    #
    headers = { "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15",
            "Accept-Language": "en-us",
            "Connection": "keep-alive" }

    conn.request("GET", p.path, headers=headers)
    response = conn.getresponse()
    #
    result = response.read().decode('utf-8') if response.status == 200 else None
    conn.close()
    #
    return result

if __name__ == "__main__":
    #
    html = getPage('https://www.howtostudykorean.com/unit1/unit-1-lessons-9-16/lesson-15/')
    #
    soup = BeautifulSoup(html, 'html.parser')
    #
    for ts in soup.findAll('span', tabindex=True):
        print("\n\n----------------")
        print("** ", ts.attrs['title'])
        d = soup.find('div', id="target-" + ts.attrs['id'])
        print(d)
