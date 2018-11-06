#encoding: utf-8
from colorama import Fore, Back, Style, init

init(autoreset=True)

class ColorHelper:
    @classmethod
    def print(cls, text, wrap):
        print(text) if wrap else print(text, end='')

    @classmethod
    def print_red(cls, text, wrap = True):
        cls.print(Fore.RED + str(text), wrap)
        
    @classmethod
    def print_green(cls, text, wrap = True):
        cls.print(Fore.GREEN + str(text), wrap)
    
    @classmethod
    def print_blue(cls, text, wrap = True):
        cls.print(Fore.BLUE + str(text), wrap)
    
    @classmethod
    def print_yellow(cls, text, wrap = True):
        cls.print(Fore.YELLOW + str(text), wrap)

    @classmethod
    def print_purple(cls, text, wrap = True):
        cls.print(Fore.MAGENTA + str(text), wrap)

    @classmethod
    def print_cyan(cls, text, wrap = True):
        cls.print(Fore.CYAN + str(text), wrap)

    @classmethod
    def print_black(cls, text, wrap = True):
        cls.print(Fore.BLACK + str(text), wrap)

    @classmethod
    def print_white(cls, text, wrap = True):
        cls.print(Fore.WHITE + str(text), wrap)
