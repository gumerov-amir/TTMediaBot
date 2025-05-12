#!/usr/bin/env python3

import os
import platform
import re
import shutil
import sys

import bs4
import patoolib
import requests

path = os.path.dirname(os.path.realpath(__file__))
path = os.path.dirname(path)
sys.path.append(path)
import downloader

url = "https://sourceforge.net/projects/mpv-player-windows/files/libmpv/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
}


def get_page(url):
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.text


def get_redirect_url(content):
    bs = bs4.BeautifulSoup(content, features="html.parser")
    meta_refresh = bs.find("meta", attrs={"http-equiv": "refresh"}).get("content")
    return meta_refresh.split("url=")[1]


def download() -> None:
    downloads = get_page(url)
    page = bs4.BeautifulSoup(downloads, features="html.parser")
    table = page.find("table")
    if platform.architecture()[0][0:2] == "64":
        version_url = table.find("a", href=True, title=re.compile("x86_64-[^v]")).get(
            "href",
        )
    else:
        version_url = table.find("a", href=True, title=re.compile("i686-")).get("href")
    download_page = get_page(version_url)
    download_url = get_redirect_url(download_page)
    downloader.download_file(download_url, os.path.join(path, "libmpv.7z"))


def extract() -> None:
    temp_path = os.path.join(path, "libmpv")
    try:
        os.mkdir(temp_path)
    except FileExistsError:
        shutil.rmtree(temp_path)
        os.mkdir(temp_path)
    patoolib.extract_archive(
        os.path.join(path, "libmpv.7z"),
        outdir=temp_path,
    )


def move_file() -> None:
    source = os.path.join(path, "libmpv", "libmpv-2.dll")
    dest = os.path.join(path, "mpv.dll")
    if os.path.exists(dest):
        os.remove(dest)
    shutil.move(source, dest)


def clean() -> None:
    os.remove(os.path.join(os.getcwd(), "libmpv.7z"))
    shutil.rmtree(os.path.join(os.getcwd(), "libmpv"))


def install() -> None:
    if sys.platform != "win32":
        sys.exit("This script should be run only on Windows")
    download()
    extract()
    move_file()
    clean()


if __name__ == "__main__":
    install()
