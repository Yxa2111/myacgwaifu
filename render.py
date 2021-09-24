import os
import subprocess
from typing import *
from collections import namedtuple
from bs4 import BeautifulSoup
from bs4.element import Comment
from waifulistParser import Append, Waifu, parseWaifu
from type import *
import re
import time
import cloudscraper

scraper = cloudscraper.create_scraper()

def readtext(path) -> str:
    if not os.path.exists(path):
        return ''
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def appendtext(path, data):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(data)

mdTpl = readtext('template.md')
mdName = 'waifu.md'

def getHTML(cid: str) -> BeautifulSoup:
    # p = subprocess.Popen(['curl', 'https://bgm.tv/character/{}'.format(cid), '-v', '--retry-delay', '10', '--proxy', 'http://172.18.208.1:1091'], stdout=subprocess.PIPE)
    # p.wait()
    # stdout, _ = p.communicate()
    # html = stdout
    html = scraper.get('https://bgm.tv/character/{}'.format(cid), proxies={
        'http': 'http://172.18.208.1:1091',
        'https': 'http://172.18.208.1:1091'
    }).content
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def parseName(soup: BeautifulSoup) -> Tuple[str, str]:
    name = soup.find_all('h1', class_='nameSingle')[0].a
    chName = name['title']
    name = name.string
    return name, chName

waifuList = set()
def loadWaifuList():
    text = readtext(mdName)
    for l in text.splitlines():
        m = re.match('> uid:([^\n]+)', l)
        if m == None:
            continue
        waifuList.add(m.group(1))

def waifuExist(w: Waifu) -> bool:
    return w.nickname in waifuList

def parseInfo(soup: BeautifulSoup) -> List[InfoKV]:
    box = soup.find_all('ul', id='infobox')[0]
    ret = []
    d = dict()
    for li in box.find_all('li'):
        k = li.span.string
        v = li.span.next_sibling
        if k not in d:
            d[k] = []
        d[k].append(v)
    
    for k, v in d.items():
        ret.append((k, v))
    return ret

def parseDetail(soup: BeautifulSoup) -> Paragraph:
    detail = soup.find_all('div', class_='detail')[0]
    ret = []
    for p in detail:
        if p.name == 'br':
            continue
        ret.append(p)
    return ret

def parseImg(soup: BeautifulSoup) -> str:
    box = soup.find_all('div', class_='infobox')[0]
    return "https:" + box.div.find_all('a')[0]['href']

def parseCV(soup: BeautifulSoup) -> str:
    list = soup.find_all('ul', class_='browserList')[0]
    alist = list.find_all('a', href=re.compile('/person/\d+'))
    if len(alist) == 0:
        return ''
    return alist[0]['title']

def getInfoFromBgm(cid: str) -> Character:
    soup = getHTML(cid)
    ret = Character(parseName(soup), parseInfo(soup), parseDetail(soup), parseImg(soup), parseCV(soup))
    return ret

def getCharacterInfo(source: Tuple[str, str]) -> Character:
    if source[0] == 'bgm':
        return getInfoFromBgm(source[1])

def compileToMd(w: Waifu, mdTpl: str) -> str:
    infolist = []
    for infokv in w.character.info:
        i = 0
        while i < len(infokv[1]):
            s = ""
            if i > 0:
                s += '\t- {}'.format(infokv[1][i])
            else:
                s += '- {} {}'.format(infokv[0], infokv[1][i])
            infolist.append(s)
            i += 1
    infolist = '\n'.join(infolist)
    detail = '\n\n'.join(w.character.detail)
    mdTpl = mdTpl.format(nickname=w.nickname, name="{}/{}".format(*w.character.name),
        infolist=infolist, img=w.character.img, detail=detail, comment="\n\n".join(w.comment), cv=w.character.CV)
    return mdTpl

def main():
    loadWaifuList()
    waifulist = readtext('waifulist.yxaa')
    waifulist = parseWaifu(waifulist)
    waifuMd = []
    for w in waifulist:
        print(w.nickname)
        if waifuExist(w):
            continue
        w.character = getCharacterInfo(w.source)
        waifuMd.append(compileToMd(w, mdTpl))
        time.sleep(5)
    waifuMd = '\n'.join(waifuMd)
    appendtext(mdName, waifuMd)

main()