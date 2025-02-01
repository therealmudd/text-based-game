import os
from typing import Any

class Console:
    def __init__(self):
        self.height = 10
        self.data = ["" for _ in range(self.height)]
    
    def print(self, *args: list[Any], join = " "):
        self.data.pop(0)
        self.data.append(join.join(map(str, args)))
        os.system("cls")
        print("\n".join(self.data))

    def debug(self, *args: list[Any], join = " "):
        to_debug = lambda x: f"\033[31m\033[3m{x}\033[0m"
        args = list(map(to_debug, args))
        self.print(*args, join = join)

    def gray_out(self):
        for i in range(self.height):

            self.data[i] = "\033[90m" + self.data[i] + "\033[0m"

    def input(self, text: str):
        return input("\033[3m" + text + "\033[0m")
