from type import Character, Paragraph
from typing import *
import re

class Waifu:
    nickname: str
    source: Tuple[str, str]
    comment: Paragraph
    character: Character
    def __init__(self) -> None:
        self.nickname = ''
        self.source = ()
        self.comment = []
        self.character = None


#Waifu = namedtuple('Waifu', ['nickname', 'source', 'comment', 'character'])
prefix = re.compile(r" +⭐")
def removeComment(s: str) -> str:
    res = re.search(prefix, s)
    if not res:
        return s
    pos = res.start()
    return s[:pos]

def removePrefix(s: str, prefix: str) -> Tuple[bool, str]:
    if s.startswith(prefix):
        pos = s.find(prefix)
        return (True, s[pos + len(prefix):])
    else:
        return (False, '')

def Append(lst, w):
    if w.nickname == '':
        return
    lst.append(w)

def parseWaifu(s: str) -> List[Waifu]:
    w = Waifu()
    ret = []
    status = 0
    for line in s.splitlines():
        line = removeComment(line)
        #ignore empty line
        if len(line) == 0:
            status = 0
            continue
        if line.startswith('@'):
            Append(ret, w)
            w = Waifu()
            w.nickname = line.split('@')[1]
            status = 1
        # source
        elif status == 1:
            w.source = line.split(':')
            status = 2
        elif status == 2:
            exist, s = removePrefix(line, 'yxaa say:')
            if not exist:
                exist, s = removePrefix(line, '\t')
                if not exist:
                    Append(ret, w)
                    w = Waifu()
                    status = 0
                    continue
            if not w.comment:
                w.comment = []
            w.comment.append(s)
    # append last waifu
    Append(ret, w)
    return ret

# s = '''@星酱 ⭐ this is unique id as so as nickname
# bgm:23243 ⭐ source {source}:{id}

# ⭐不同人物之间会隔1到多个空行
# @233 ⭐ this is unique id as so as nickname
# bgm:23243 ⭐ source {source}:{id}
# '''

#print(parseWaifu(s))
