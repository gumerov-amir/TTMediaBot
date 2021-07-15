#!/usr/bin/env python3

import os
import platform
import shutil
import sys
from urllib import request

import bs4
import patoolib

url = "https://sourceforge.net/projects/mpv-player-windows/files/libmpv/"

cd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def download():
    r = request.urlopen(url)
    page = bs4.BeautifulSoup(r.read().decode("utf-8"), features="html.parser")
    trs = page.table.find_all("tr")
    if platform.architecture()[0][0:2] == "64":
        download_url = trs[2].a.get("href")
    else:
        download_url = trs[3].a.get("href")
    request.urlretrieve(download_url, os.path.join(cd, "libmpv.7z"))

def extract():
    try:
        os.mkdir(os.path.join(cd, 'libmpv'))
    except FileExistsError:
        shutil.rmtree(os.path.join(cd, 'libmpv'))
        os.mkdir(os.path.join(cd, 'libmpv'))
    patoolib.extract_archive(os.path.join(cd, 'libmpv.7z'), outdir=os.path.join(cd, 'libmpv'))

def move():
    try:
        os.rename(os.path.join(cd, "libmpv", "mpv-1.dll"), os.path.join(cd, "mpv-1.dll"))
    except FileExistsError:
        os.remove(os.path.join(cd, "mpv-1.dll"))
        os.rename(os.path.join(cd, "libmpv", "mpv-1.dll"), os.path.join(cd, "mpv-1.dll"))

def clean():
    os.remove(os.path.join(cd, "libmpv.7z"))
    shutil.rmtree(os.path.join(cd, "libmpv"))

def install():
    print('Installing mpv components')
    print('Downloading latest libmpv version')
    download()
    print('Downloaded. extracting')
    extract()
    print('Extracted. moving')
    move()
    print('moved. cleaning')
    clean()
    print('cleaned.')
    print('Installed')

if __name__ == "__main__":
    install()
