#!/usr/bin/env python3

import bs4
import patoolib
import requests

import os
import platform
import re
import shutil
import sys

path = os.path.dirname(os.path.realpath(__file__))
path = os.path.dirname(path)
sys.path.append(path)
import downloader


url = "https://sourceforge.net/projects/mpv-player-windows/files/libmpv/"


def download():
    try:
        r = requests.get(url)
        r.raise_for_status() # raise an error if there was a problem with the request
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return
    
    page = bs4.BeautifulSoup(r.text, features="html.parser")
    table = page.find("table")
    
    if platform.architecture()[0][0:2] == "64":
        download_url = table.find("a", href=True, title=re.compile("x86_64")).get("href")
    else:
        download_url = table.find("a", href=True, title=re.compile("i686")).get("href")
    
    try:
        downloader.download_file(download_url, os.path.join(os.getcwd(), "libmpv.7z"))
    except Exception as e:
        print(f"Error downloading file: {e}")


def extract():
    try:
        os.mkdir(os.path.join(os.getcwd(), "libmpv"))
    except FileExistsError:
        shutil.rmtree(os.path.join(os.getcwd(), "libmpv"))
        os.mkdir(os.path.join(os.getcwd(), "libmpv"))
    try:
        patoolib.extract_archive(
            os.path.join(os.getcwd(), "libmpv.7z"),
            outdir=os.path.join(os.getcwd(), "libmpv"),
        )
    except Exception as e:
        print(f"Error extracting file: {e}")
        return

def move():
    try:
        source = os.path.join(os.getcwd(), "libmpv", "libmpv-2.dll")
        dest = os.path.join(os.getcwd(), "mpv.dll")
        if not os.path.exists(source):
            raise FileNotFoundError("The file mpv-2.dll does not exist")
            return
        elif os.path.exists(dest):
            os.remove(dest)
        os.rename(source, dest)
    except (FileNotFoundError, FileExistsError, Exception) as e:
        print(f"Error moving file: {e}")

def clean():
    os.remove(os.path.join(os.getcwd(), "libmpv.7z"))
    shutil.rmtree(os.path.join(os.getcwd(), "libmpv"))


def install():
    if sys.platform != "win32":
        sys.exit("This script should be run only on Windows")
    print("Installing libmpv for Windows")
    print("Downloading latest libmpv version")
    download()
    print("Downloaded. extracting")
    extract()
    print("Extracted. moving")
    move()
    print("moved. cleaning")
    clean()
    print("cleaned.")
    print("Installed")


if __name__ == "__main__":
    install()
