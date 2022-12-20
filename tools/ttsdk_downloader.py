#!/usr/bin/env python3

import bs4
import patoolib
import requests

import os
import platform
import shutil
import sys

path = os.path.dirname(os.path.realpath(__file__))
path = os.path.dirname(path)
sys.path.append(path)
import downloader


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
            sys.exit("Native Windows on ARM is not supported")
    elif sys.platform == "darwin":
        sys.exit("Darwin is not supported")
    else:
        if machine == "AMD64" or machine == "x86_64":
            return "ubuntu22_x86_64"
        elif "arm" in machine:
            return "raspbian_armhf"
        else:
            sys.exit("Your architecture is not supported")


def download() -> None:
    r = requests.get(url)
    page = bs4.BeautifulSoup(r.text, features="html.parser")
    # The last tested version is 5.11
    versions = page.find_all("li")
    version = [i for i in versions if "5.11" in i.text][-1].a.get("href")[0:-1]
    download_url = (
        url
        + "/"
        + version
        + "/"
        + "tt5sdk_{v}_{p}.7z".format(v=version, p=get_url_suffix_from_platform())
    )
    print("Downloading from " + download_url)
    downloader.download_file(download_url, os.path.join(cd, "ttsdk.7z"))


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
    libraries = ["TeamTalk_DLL", "TeamTalkPy"]
    for library in libraries:
        try:
            os.rename(
                os.path.join(path, "Library", library), os.path.join(cd, library)
            )
        except OSError:
            shutil.rmtree(os.path.join(cd, library))
            os.rename(
                os.path.join(path, "Library", library), os.path.join(cd, library)
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
