from pyfiglet import Figlet
from termcolor import colored  
import os
import time
import random


def print_line():
    line = 66*'+'
    for char in line:
        c = 'cyan'
        print(colored(char, c), end='', flush=True)
        time.sleep(0.000001)
    print()


print_line()
f = Figlet(font='slant')
logo = colored(f.renderText(' Excel  Finder '), 'cyan')
print(logo)

# 计算technology右侧对齐需要的空格数
space_count = 30
# 打印空格
print(" " * space_count, end='')

name = "Vincent @ZhengYang Technology"
# colors = ['white','green','blue','cyan']
colors = ['white','red','green','yellow','blue','magenta','cyan']
last_color = None
for char in name:
    while True:
        c = random.choice(colors)
        if c != last_color:
            break
    last_color = c
    print(colored(char, c), end='', flush=True)
    time.sleep(0.00001)
print()

print_line()

# print(colored('*** Welcome to Use My Code ***', 'magenta'))

while True:
    os.system('python finder.py')
    
    choice = input('是否需要再次生成新的报价?默认Y继续, (Y/N)')
    
    if choice.upper() == 'n':
        break
        
os.system('pause')
