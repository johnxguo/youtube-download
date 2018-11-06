#author: johnxguo
#date: 2018-10-28

import os
from colorama import Fore, Back, Style, init

init(autoreset=True)

try:
    1 / 0
except Exception as err:
    print(Fore.GREEN + err)