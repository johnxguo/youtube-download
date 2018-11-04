#encoding: utf-8
from colorama import Fore, Back, Style, init

init(autoreset=True)

class ColorHelper:
    @classmethod
    def print(cls, text, wrap):
        print(text) if wrap else print(text, end='')

    @classmethod
    def print_red(cls, text, wrap = True):
        cls.print(Fore.RED + text, wrap)
        
    @classmethod
    def print_green(cls, text, wrap = True):
        cls.print(Fore.GREEN + text, wrap)
    
    @classmethod
    def print_blue(cls, text, wrap = True):
        cls.print(Fore.BLUE + text, wrap)
    
    @classmethod
    def print_yellow(cls, text, wrap = True):
        cls.print(Fore.YELLOW + text, wrap)

    @classmethod
    def print_purple(cls, text, wrap = True):
        cls.print(Fore.MAGENTA + text, wrap)

    @classmethod
    def print_cyan(cls, text, wrap = True):
        cls.print(Fore.CYAN + text, wrap)

    @classmethod
    def print_black(cls, text, wrap = True):
        cls.print(Fore.BLACK + text, wrap)

    @classmethod
    def print_white(cls, text, wrap = True):
        cls.print(Fore.WHITE + text, wrap)
