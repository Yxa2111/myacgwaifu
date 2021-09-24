from typing import *
from collections import namedtuple

Character = namedtuple('character', ['name', 'info', 'detail', 'img','CV'])
Paragraph = List[str]
InfoKV = Tuple[str, List[str]]