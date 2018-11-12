#author: johnxguo
#date: 2018-10-31

from enum import Enum, unique

@unique
class LoginState(Enum):
    logout = 0
    login_process = 1
    login_fail = 2
    login_succ = 3