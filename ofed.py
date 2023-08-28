#!/usr/bin/python3
# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
from tqdm import tqdm
from pathlib import Path
import requests
import subprocess
import time
import re

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://downloaders.azurewebsites.net/downloaders/mlnx_ofed_downloader/downloader3.html')

    # 等待第1部分页面加载完成
    page.wait_for_load_state()
    time.sleep(3)
    page.wait_for_load_state()
    
    elements1 = []
    for el in page.query_selector_all(".version.show_on_current"):
        text = el.inner_text()
        elements1.append((text, el))
    # 打印第1部分 内容
    print("当前驱动版本：")
    for i, (text, el) in enumerate(elements1):
        print(f"{i+1}. {text}")
    choice = int(input("请选择驱动版本:"))
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
    print("\n支持的操作系统：")
    for i, (text, el) in enumerate(elements2):
        print(f"{i+1}. {text}")
    choice = int(input("请选择操作系统:"))
    selected_text, selected_el = elements2[choice-1]
    selected_el.click()

    # 等待第3部分页面加载完成
    page.wait_for_selector(".os", state="visible")
    elements3 = []
    for el in page.query_selector_all(".os"):
        text = el.inner_text()
        elements3.append((text, el))
    # 打印第3部分 内容
    print("\n操作系统版本号：")
    for i, (text, el) in enumerate(elements3):
        print(f"{i+1}. {text}")
    choice = int(input("请选择操作系统版本号:"))
    selected_text, selected_el = elements3[choice-1]
    selected_el.click()

    # 等待第4部分页面加载完成
    page.wait_for_selector(".arch", state="visible")

    elements4 = []
    for el in page.query_selector_all(".arch"):
        text = el.inner_text()
        elements4.append((text, el))
    # 打印第4部分 内容
    print("\n架构：")
    for i, (text, el) in enumerate(elements4):
        print(f"{i+1}. {text}")
    choice = int(input("请选择架构:"))
    selected_text, selected_el = elements4[choice-1]
    selected_el.click()

    # 等待第5部分页面加载完成
    page.wait_for_selector(".info", state="visible")
    elements5 = []
    texts = []
    for el in page.query_selector_all(".info"):
        text = el.inner_text()
        texts.append(text)
        elements5.append((text, el))
    # 打印download 表格信息
    with open("download_info.txt", "w") as f:
        f.write("\n".join(texts))
    path_iso = ""
    path_tgz = ""
    a_links = "https://content.mellanox.com/ofed/MLNX_OFED-"
    pattern = r'\d+\.\d+-\d+\.\d+\.\d+\.\d+'
    version_iso = ""
    version_tgz = ""
    version_zip = ""
    file_name_iso = ""
    file_name_tgz = ""
    file_name_zip = ""
    # print("\n驱动安装包文件：")
    with open("download_info.txt") as f:
        for line in f:
            if "ISO:" in line:
                path_iso = line.strip()
                version_iso_re = re.search(pattern, path_iso)
                # print(line.strip())
                file_name_iso = line.strip().split(": ")[1]
                # print(file_name_iso)
                version_iso = version_iso_re.group(0)
            elif "tgz:" in line:
                path_tgz = line.strip()
                version_tgz_re = re.search(pattern, path_tgz)
                # print(line.strip())
                file_name_tgz = line.strip().split(": ")[1]
                # print(file_name_tgz)
                version_tgz = version_tgz_re.group(0)
            elif ".zip:" in line:
                path_zip = line.strip()
                version_zip_re = re.search(pattern, path_zip)
                # print(line.strip())
                file_name_zip = line.strip().split(": ")[1]
                # print(file_name_tgz)
                version_zip = version_zip_re.group(0)

    # print(version_iso)
    download_link_iso = a_links + version_iso + "/" + file_name_iso
    download_link_tgz = a_links + version_iso + "/" + file_name_tgz
    print("\n输出下载链接：")
    print(download_link_iso)
    print(download_link_tgz)
    browser.close()
    sub_dir = 'html/ofed'
    ret = subprocess.run(['mkdir','-p', sub_dir])
    if ret.returncode == 0:
        print(f'{sub_dir} created successfully!')
    ret = subprocess.run(['pwd'], capture_output=True)
    html_dir = ret.stdout.decode().strip() + '/' + sub_dir
    with open(html_dir + "/index.html", 'w') as f:
        f.write(download_link_iso)
        f.write("\n")
    ret = subprocess.run(['rm','-rf', "download_info.txt"])
    

#    url = download_link_iso
#    down_request = input("\n是否需要下载文件？（y/n）")
#    if down_request == "y" or down_request == "Y":
#        response = requests.get(url, stream=True)
#        total_size_in_bytes = int(response.headers.get('content-length', 0))
#        block_size = 1024
#        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
#        with open("html/ofed/" + file_name_iso, "wb") as f:
#            for data in response.iter_content(block_size):
#                progress_bar.update(len(data))
#                f.write(data)
#        progress_bar.close()
#        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
#            print("ERROR, something went wrong")
#        else:
#            print("文件下载完毕!")
#            #print("下载链接：\nnvlink.vip/ofed/" + file_name_iso)
#            print("下载链接：\n52.53.194.118/ofed/" + file_name_iso)
