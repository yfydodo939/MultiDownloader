import os
import threading
from time import sleep

import requests

url = input("请输入下载链接: \n> ")
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 "
                  "Safari/537.36"
}
fileName = url.split('/')[-1].split('?')[0]
session = requests.Session()

try:
    info = requests.head(url)
    size = int(info.headers.get('Content-Length'))
except:
    input("文件不支持多线程下载 或 链接有误, 请移步至浏览器进行下载\n按Enter退出")
    raise ValueError
if size < 1024:
    print("文件大小 > %d B < " % size)
elif 1024 <= size < 1024 ** 2:
    print("文件大小 > %.2f KB < " % (size / 1024))
elif 1024 ** 2 <= size < 1024 ** 3:
    print("文件大小 > %.2f MB < " % (size / 1024 ** 2))
else:
    print("文件大小 > %.2f GB < " % (size / 1024 ** 3))
THREAD = int(input(f"即将下载 > {fileName} < \n请输入线程数(1-256): "))
if THREAD == 1:
    single = size
elif 2 <= THREAD <= 256:
    single = size // (THREAD - 1)
else:
    input("线程数输入有误, 按Enter退出")
    raise ValueError()
_headers = headers.copy()
S = 0
print()


def download(count):
    global S
    __headers = _headers.copy()
    start = int(count * single)
    end = int(start + single - 1)
    if end > size:
        end = size
    __headers["Range"] = f"bytes={start}-{end}"
    with open(f"cache\\{count}.part", "wb") as f:
        f.write(session.get(url=url, headers=__headers, stream=True).content)
    S += 1


try:
    os.mkdir("cache")
except FileExistsError:
    pass
for i in range(THREAD):
    threading.Thread(target=download, args=(i,)).start()

while True:
    if S == THREAD:
        print(f"\r{THREAD}/{THREAD}已完成 [ 100.0% ]\n\n正在合并文件......", end="")
        fp = open(fileName, "wb")
        for i in range(THREAD):
            fp.write(open(f"cache\\{i}.part", "rb").read())
        fp.close()
        print("完成\n正在删除临时文件......", end="")
        for j in range(THREAD):
            os.remove(f"cache\\{j}.part")
        print("完成")
        break
    else:
        print("\r%d/%d已完成 [ %.1f%% ]" % (S, THREAD, S / THREAD * 100), end="")
        sleep(0.2)
        continue
input("文件已保存至 > " + os.getcwd() + "\\" + fileName + " < \n按Enter退出")
