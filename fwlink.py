#!/usr/bin/python3
from playwright.sync_api import sync_playwright
from tqdm import tqdm
from pathlib import Path
import requests
import subprocess
import time
import re
from fw_link_data import fw_link_data 

print(""" 1: bf3
 2: bf2
 3: cx7
 4: cx6de
 5: cx6lx
 6: cx6dx
 7: cx6en
 8: cx6ib
 9: cx5en
10: cx5ib
11: cx4lx
12: cx4en
13: cx4ib
14: cx3proen
15: cx3proib
16: cx3en
17: cx3ib
18: quantum2
19: quantum
20: switchib2
21: switchib
        """)
pn_select = int(input('Enter a number: '))
pn = fw_link_data[pn_select]
model = pn['model']
url = pn['link']

#print(url)
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url)

    # 等待第1部分页面加载完成
    page.wait_for_load_state()
    time.sleep(5)
    page.wait_for_load_state()
    
    elements1 = []
    for el in page.query_selector_all(".version.currentcss"):
        text = el.inner_text()
        elements1.append((text, el))
    # 打印第1部分 内容
    print("当前固件版本：")
    for i, (text, el) in enumerate(elements1):
        print(f"{i+1}. {text}")
    choice = int(input("请选择固件版本:"))
    selected_text, selected_el = elements1[choice-1]
    selected_el.click()

    # 等待第2部分页面加载完成
    # 等待元素出现并且可见
    page.wait_for_selector(".distro", state="visible")

    # 等待元素出现并且启用
    # page.wait_for_selector(".distro", state="enabled")

    elements2 = []
    for el in page.query_selector_all(".distro"):
        text = el.inner_text()
        elements2.append((text, el))
    # 打印第2部分 内容
    print("\n支持的OPN：")
    for i, (text, el) in enumerate(elements2):
        print(f"{i+1}. {text}")
    choice = int(input("请选择OPN:"))
    selected_text, selected_el = elements2[choice-1]
    selected_el.click()

    # 等待第3部分页面加载完成
    page.wait_for_selector(".os", state="visible")
    elements3 = []
    for el in page.query_selector_all(".os"):
        text = el.inner_text()
        elements3.append((text, el))
    # 打印第3部分 内容
    print("\nPSID：")
    for i, (text, el) in enumerate(elements3):
        print(f"{i+1}. {text}")
    choice = int(input("请选择PSID:"))
    selected_text, selected_el = elements3[choice-1]
    selected_el.click()

    # 等待第4部分页面加载完成
#    page.wait_for_selector(".arch", state="visible")
#
#    elements4 = []
#    for el in page.query_selector_all(".arch"):
#        text = el.inner_text()
#        elements4.append((text, el))
#    # 打印第4部分 内容
#    print("\n架构：")
#    for i, (text, el) in enumerate(elements4):
#        print(f"{i+1}. {text}")
#    choice = int(input("请选择架构:"))
#    selected_text, selected_el = elements4[choice-1]
#    selected_el.click()

    # 等待第5部分页面加载完成
    page.wait_for_selector(".info", state="visible")
    elements5 = []
    texts = []
    for el in page.query_selector_all(".info"):
        text = el.inner_text()
        texts.append(text)
        elements5.append((text, el))
    # 打印download 表格信息
    folder = "html/" + model
    ret = subprocess.run(['mkdir', '-p', folder])
    if ret.returncode == 0:
        print(f'{folder} folder created successfully!')
    else:
        print(f'Failed to create {folder} folder')
    info = model + "info.txt"
    with open(info, "w") as f:
        f.write("\n".join(texts))
    file_name_zip = ""
    a_link = "https://www.mellanox.com/downloads/firmware/"
    e_link = ".bin.zip"
    with open(info) as f:
        for line in f:
            if "fw-" in line:
                # print(line.strip())
                file_name_zip = line.strip().split(": ")[1]
                #print(file_name_zip)

    print("\n输出下载链接：")
    file_name_zip = a_link + file_name_zip + e_link
    print(file_name_zip)
    browser.close()
    
    with open(f"html/{model}/index.html", 'w') as f:
        f.write(file_name_zip)
        f.write("\n")
    ret = subprocess.run(['rm', info])
