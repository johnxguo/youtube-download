#encoding: utf-8
import ctypes
 
STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE= -11
STD_ERROR_HANDLE = -12
 
FOREGROUND_BLACK = 0x0
FOREGROUND_BLUE = 0x01 # text color contains blue.
FOREGROUND_GREEN= 0x02 # text color contains green.
FOREGROUND_RED = 0x04 # text color contains red.
FOREGROUND_INTENSITY = 0x08 # text color is intensified.
 
BACKGROUND_BLUE = 0x10 # background color contains blue.
BACKGROUND_GREEN= 0x20 # background color contains green.
BACKGROUND_RED = 0x40 # background color contains red.
BACKGROUND_INTENSITY = 0x80 # background color is intensified.
 
class WinColor:
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    @classmethod
    def set_text_color(cls, color, handle=std_out_handle):
        return ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)

    @classmethod
    def reset_text_color(cls):
        cls.set_text_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)

    @classmethod
    def print(cls, text, wrap):
        print(text) if wrap else print(text, end='')

    @classmethod
    def print_red(cls, text, wrap = True):
        cls.set_text_color(FOREGROUND_RED | FOREGROUND_INTENSITY)
        cls.print(text, wrap)
        cls.reset_text_color()
        
    @classmethod
    def print_green(cls, text, wrap = True):
        cls.set_text_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY)
        cls.print(text, wrap)
        cls.reset_text_color()
    
    @classmethod
    def print_blue(cls, text, wrap = True):
        cls.set_text_color(FOREGROUND_BLUE | FOREGROUND_INTENSITY)
        cls.print(text, wrap)
        cls.reset_text_color()
    
    @classmethod
    def print_yellow(cls, text, wrap = True):
        cls.set_text_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_INTENSITY)
        cls.print(text, wrap)
        cls.reset_text_color()

    @classmethod
    def print_purple(cls, text, wrap = True):
        cls.set_text_color(FOREGROUND_RED | FOREGROUND_BLUE | FOREGROUND_INTENSITY)
        cls.print(text, wrap)
        cls.reset_text_color()

    @classmethod
    def print_cyan(cls, text, wrap = True):
        cls.set_text_color(FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY)
        cls.print(text, wrap)
        cls.reset_text_color()

    @classmethod
    def print_black(cls, text, wrap = True):
        cls.set_text_color(FOREGROUND_BLACK | FOREGROUND_INTENSITY)
        cls.print(text, wrap)
        cls.reset_text_color()

    @classmethod
    def print_white(cls, text, wrap = True):
        cls.set_text_color(FOREGROUND_RED | FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_INTENSITY)
        cls.print(text, wrap)
        cls.reset_text_color()
