import threading
import time
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
import os
import psutil

import requests

S = 0
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/111.0.0.0 Safari/537.36"
}
single, size = 0, 0
session = requests.Session()
try:
    os.mkdir("cache")
except:
    pass


def download(count):
    global S, size, session
    _headers = headers.copy()
    start = int(count * single)
    end = int(start + single - 1)
    if end > size:
        end = size
    _headers["Range"] = f"bytes={start}-{end}"
    with open(f"cache\\{count}.part", "wb") as f:
        f.write(session.get(url=url_entry.get(), headers=_headers, stream=True).content)
    S += 1


def download_start():
    THREAD = int(thread.get())
    global single
    if THREAD == 1:
        single = size
    elif 2 <= THREAD <= 256:
        single = size // (THREAD - 1)
    download_button.config(state="disabled")
    progressbar.config(maximum=THREAD)
    for i in range(THREAD):
        threading.Thread(target=download, args=(i,)).start()
    while True:
        progressbar.config(value=S)
        if S == THREAD:
            state_str.set("正在合并文件...")
            fp = open(filename_str.get(), "wb")
            for i in range(THREAD):
                fp.write(open(f"cache\\{i}.part", "rb").read())
            fp.close()
            state_str.set("正在删除临时文件...")
            for j in range(THREAD):
                os.remove(f"cache\\{j}.part")
            state_str.set("文件已保存至同级目录内")
            tkinter.messagebox.showinfo("下载完成", "文件已保存至" + os.getcwd() + "\\" + filename_str.get())
            break
        else:
            state_str.set("%.1f%%\t%d/%d" % (S / THREAD * 100, S, THREAD))
            time.sleep(0.2)
            continue


def net_check():
    _, ___ = 0, 0
    while True:
        ___ = psutil.net_io_counters().bytes_recv
        __ = ___ - _
        _ = ___
        if 0 <= __ < 1024 ** 2:
            __ = "%.1fKB/s" % (__ / 1024 * 2)
        elif 1024 ** 2 <= __ < 1024 ** 3:
            __ = "%.1fMB/s" % (__ / 1024 ** 2 * 2)
        elif 1024 ** 3 <= __:
            __ = "%.1GB/s" % (__ / 1024 ** 3 * 2)
        else:
            __ = "N/A"
        net_str.set(__)
        time.sleep(0.5)


def setico():
    try:
        try:
            window.iconphoto(True, tk.PhotoImage(file="icon.png"))
        except:
            with open("icon.png", "wb") as fp:
                fp.write(requests.get(
                    "https://images.weserv.nl/?url=https://article.biliimg.com/bfs/article"
                    "/fa07c627ce5090d5595f4889032da04bff3e484b.png").content)
            window.iconphoto(True, tk.PhotoImage(file="icon.png"))
    except:
        pass


def ontop():
    while True:
        if isOnTop.get() == 1:
            window.attributes("-topmost", True)
        else:
            window.attributes("-topmost", False)
        time.sleep(0.2)


def detect():
    global headers, size
    try:
        url = url_entry.get()
        fileName = url.split('/')[-1].split('?')[0]
        if fileName == "":
            fileName = "default"
        info = requests.head(url)
        size = int(info.headers.get('Content-Length'))
        if size < 1024:
            size_str.set("%dB" % size)
        elif 1024 <= size < 1024 ** 2:
            size_str.set("%.2fKB" % (size / 1024))
        elif 1024 ** 2 <= size < 1024 ** 3:
            size_str.set("%.2fMB" % (size / 1024 ** 2))
        else:
            size_str.set("%.2fGB" % (size / 1024 ** 3))
        filename_str.set(fileName)
        download_button.config(state="enabled")
        url_entry.config(state="readonly")
        detect_button.config(state="disabled")
    except:
        tkinter.messagebox.showerror("错误", "文件不支持多线程下载或链接有误, 请移步至浏览器进行下载")


window = tk.Tk()
window.title("MultiDownloader by dodo939")
window.geometry("400x225")
window.resizable(width=False, height=False)

frame1 = tk.Frame()
frame1.grid(padx=10, pady=5, row=0)
ttk.Label(frame1, text="文件名", padding=8).grid(row=0, column=0, sticky="w")
ttk.Label(frame1, text="下载链接", padding=8).grid(row=1, column=0, sticky="w")
ttk.Label(frame1, text="文件大小", padding=8).grid(row=2, column=0, sticky="w")
size_str = tk.StringVar()
size_str.set("0B")
size_label = ttk.Label(frame1, textvariable=size_str, padding=8)
size_label.grid(row=2, column=1, sticky="w")
isOnTop = tk.IntVar()
onTop = ttk.Checkbutton(frame1, text="保持窗口置顶", variable=isOnTop, onvalue=1, offvalue=0)
onTop.grid(row=2, column=3, sticky="w")
isOnTop.set(0)

filename_str = tk.StringVar()
filename_entry = ttk.Entry(frame1, textvariable=filename_str, width=40, state="readonly")
filename_entry.grid(row=0, column=1, padx=10, columnspan=3)
url_entry = ttk.Entry(frame1, width=40)
url_entry.grid(row=1, column=1, padx=10, columnspan=3)

frame2 = tk.Frame()
frame2.grid(padx=10, row=1, sticky="w")
ttk.Label(frame2, text="线程数", padding=8).grid(row=0, column=0)
thread = tk.StringVar()
ttk.OptionMenu(frame2, thread, "64", "1", "4", "16", "64", "128", "256").grid(row=0, column=1, padx=10, sticky="w")
detect_button = ttk.Button(frame2, text="检测", command=detect)
detect_button.grid(row=0, column=2)
download_button = ttk.Button(frame2, text="开始下载", state="disabled",
                             command=threading.Thread(target=download_start, daemon=True).start)
download_button.grid(row=0, column=3)

progressbar = ttk.Progressbar(length=360, value=0)
progressbar.grid(pady=8)

state_str = tk.StringVar()
state_str.set("0.0%\t0/0")
ttk.Label(textvariable=state_str).grid(sticky="w", padx=15)

net_str = tk.StringVar()
net_str.set("0KB/s")
ttk.Label(textvariable=net_str).grid(sticky="e", padx=15, row=3)

threading.Thread(target=ontop, daemon=True).start()
threading.Thread(target=net_check, daemon=True).start()
threading.Thread(target=setico, daemon=True).start()
url_entry.focus_set()

window.mainloop()
