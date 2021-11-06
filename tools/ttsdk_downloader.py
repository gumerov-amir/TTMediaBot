#!/usr/bin/env python3

import os
import platform
import shutil
import sys
from urllib import request

import bs4
import patoolib


url = "http://bearware.dk/teamtalksdk"

cd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_url_suffix_from_platform() -> str:
    machine = platform.machine()
    if sys.platform == "win32":
        architecture = platform.architecture()
        if machine == "AMD64" or machine == "x86":
            if architecture[0] == "64bit":
                return "win64"
            else:
                return "win32"
        else:
            sys.exit("Native Windows on ARM is not suported")
    elif sys.platform == "darwin":
        sys.exit("Darwin is not supported")
    else:
        if machine == "AMD64" or machine == "x86_64":
            return "ubuntu18_x86_64"
        elif "arm" in machine:
            return "raspbian_armhf"
        else:
            sys.exit("Your architecture is not supported")


def download() -> None:
    r = request.urlopen(url)
    html = r.read().decode("UTF-8")
    page = bs4.BeautifulSoup(html, features="html.parser")
    versions = page.find_all("li")
    last_version = versions[-1].a.get("href")[0:-1]
    download_url = (
        url
        + "/"
        + last_version
        + "/"
        + "tt5sdk_{v}_{p}.7z".format(v=last_version, p=get_url_suffix_from_platform())
    )
    print("Downloading from " + download_url)
    request.urlretrieve(download_url, os.path.join(cd, "ttsdk.7z"))


def extract() -> None:
    try:
        os.mkdir(os.path.join(cd, "ttsdk"))
    except FileExistsError:
        shutil.rmtree(os.path.join(cd, "ttsdk"))
        os.mkdir(os.path.join(cd, "ttsdk"))
    patoolib.extract_archive(
        os.path.join(cd, "ttsdk.7z"), outdir=os.path.join(cd, "ttsdk")
    )


def move() -> None:
    path = os.path.join(cd, "ttsdk", os.listdir(os.path.join(cd, "ttsdk"))[0])
    try:
        if sys.platform == "win32":
            os.rename(
                os.path.join(path, "Library/TeamTalk_DLL/TeamTalk5.dll"),
                os.path.join(cd, "TeamTalk5.dll"),
            )
        else:
            os.rename(
                os.path.join(path, "Library/TeamTalk_DLL/libTeamTalk5.so"),
                os.path.join(cd, "libTeamTalk5.so"),
            )
    except FileExistsError:
        if sys.platform == "win32":
            os.remove(os.path.join(cd, "TeamTalk5.dll"))
            os.rename(
                os.path.join(path, "Library/TeamTalk_DLL/TeamTalk5.dll"),
                os.path.join(cd, "TeamTalk5.dll"),
            )
        else:
            os.remove(os.path.join(cd, "libTeamTalk5.so"))
            os.rename(
                os.path.join(path, "Library/TeamTalk_DLL/libTeamTalk5.so"),
                os.path.join(cd, "libTeamTalk5.so"),
            )
    try:
        os.rename(
            os.path.join(path, "Library/TeamTalkPy"), os.path.join(cd, "TeamTalkPy")
        )
    except OSError:
        shutil.rmtree(os.path.join(cd, "TeamTalkPy"))
        os.rename(
            os.path.join(path, "Library/TeamTalkPy"), os.path.join(cd, "TeamTalkPy")
        )
    try:
        os.rename(
            os.path.join(path, "License.txt"), os.path.join(cd, "TTSDK_license.txt")
        )
    except FileExistsError:
        os.remove(os.path.join(cd, "TTSDK_license.txt"))
        os.rename(
            os.path.join(path, "License.txt"), os.path.join(cd, "TTSDK_license.txt")
        )


def clean() -> None:
    os.remove(os.path.join(cd, "ttsdk.7z"))
    shutil.rmtree(os.path.join(cd, "ttsdk"))


def install() -> None:
    print("Installing TeamTalk sdk components")
    print("Downloading latest sdk version")
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
