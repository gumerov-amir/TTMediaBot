#!/usr/bin/env python3

import os
import platform
import re
import shutil
import sys
from pathlib import Path

import bs4
import patoolib
import requests

import downloader

path = str(Path(os.path.realpath(__file__)).parent.parent)
sys.path.append(path)

url = "https://sourceforge.net/projects/mpv-player-windows/files/libmpv/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
}


def get_page(url: str) -> str:
    r = requests.get(url, headers=headers, timeout=60)
    r.raise_for_status()
    return r.text


def get_redirect_url(content: str | bytes) -> str:
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
    downloader.download_file(download_url, str(Path(path) / "libmpv.7z"))


def extract() -> None:
    temp_path = Path(path) / "libmpv"
    try:
        temp_path.mkdir(exist_ok=False)
    except FileExistsError:
        temp_path.unlink()
        temp_path.mkdir()
    patoolib.extract_archive(
        str(Path(path) / "libmpv.7z"),
        outdir=str(temp_path),
    )


def move_file() -> None:
    source = Path(path) / "libmpv", "libmpv-2.dll"
    dest = Path(path) / "mpv.dll"
    if dest.exists():
        dest.unlink()
    shutil.move(source, dest)


def clean() -> None:
    (Path.cwd() / "libmpv.7z").unlink(missing_ok=True)
    shutil.rmtree(Path.cwd() / "libmpv")


def install() -> None:
    if sys.platform != "win32":
        sys.exit("This script should be run only on Windows")
    download()
    extract()
    move_file()
    clean()


if __name__ == "__main__":
    install()
