#encoding: utf-8
from colorama import Fore, Back, Style, init

init(autoreset=True)

class Console:
    _continuous_id = 0

    @classmethod
    def print(cls, text, wrap, continuous_id, continuous_word):
        if continuous_id == 0 and Console._continuous_id != 0:
            Console._continuous_id = 0
            print('')
        elif continuous_id != 0 and Console._continuous_id == 0:
            Console._continuous_id = continuous_id
            wrap = False
        elif continuous_id != 0 and Console._continuous_id != 0:
            if continuous_id == Console._continuous_id:
                print(continuous_word, end='')
                return
            else:
                Console._continuous_id = continuous_id
                print('')
        print(text) if wrap else print(text, end='')

    @classmethod
    def print_red(cls, text, wrap = True, continuous_id = 0, continuous_word = ''):
        cls.print(Fore.RED + str(text), wrap, continuous_id, Fore.RED + str(continuous_word))
        
    @classmethod
    def print_green(cls, text, wrap = True, continuous_id = 0, continuous_word = ''):
        cls.print(Fore.GREEN + str(text), wrap, continuous_id, Fore.GREEN + str(continuous_word))
    
    @classmethod
    def print_blue(cls, text, wrap = True, continuous_id = 0, continuous_word = ''):
        cls.print(Fore.BLUE + str(text), wrap, continuous_id, Fore.BLUE + str(continuous_word))
    
    @classmethod
    def print_yellow(cls, text, wrap = True, continuous_id = 0, continuous_word = ''):
        cls.print(Fore.YELLOW + str(text), wrap, continuous_id, Fore.YELLOW + str(continuous_word))

    @classmethod
    def print_purple(cls, text, wrap = True, continuous_id = 0, continuous_word = ''):
        cls.print(Fore.MAGENTA + str(text), wrap, continuous_id, Fore.MAGENTA + str(continuous_word))

    @classmethod
    def print_cyan(cls, text, wrap = True, continuous_id = 0, continuous_word = ''):
        cls.print(Fore.CYAN + str(text), wrap, continuous_id, Fore.CYAN + str(continuous_word))

    @classmethod
    def print_black(cls, text, wrap = True, continuous_id = 0, continuous_word = ''):
        cls.print(Fore.BLACK + str(text), wrap, continuous_id, Fore.BLACK + str(continuous_word))

    @classmethod
    def print_white(cls, text, wrap = True, continuous_id = 0, continuous_word = ''):
        cls.print(Fore.WHITE + str(text), wrap, continuous_id, Fore.WHITE + str(continuous_word))
