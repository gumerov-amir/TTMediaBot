#!/usr/bin/env python3

import bs4
import cloudscraper
import patoolib

import os
import platform
import shutil
import sys

path = os.path.dirname(os.path.realpath(__file__))
path = os.path.dirname(path)
sys.path.append(path)
import downloader


url = "https://bearware.dk/teamtalksdk"

# Minimum glibc versions shipped by the Ubuntu releases used in SDK file names,
# used to skip builds the local runtime cannot load
UBUNTU_GLIBC = {"22": (2, 35), "24": (2, 39), "26": (2, 43)}


def get_platform_tokens():
    machine = platform.machine()
    if sys.platform == "win32":
        architecture = platform.architecture()
        if machine == "AMD64" or machine == "x86":
            if architecture[0] == "64bit":
                return ["win64"]
            else:
                return ["win32"]
        else:
            sys.exit("Native Windows on ARM is not supported")
    elif sys.platform == "darwin":
        sys.exit("Darwin is not supported")
    else:
        if machine == "AMD64" or machine == "x86_64":
            # The Ubuntu release in the file name changed across SDK versions
            # (ubuntu22/ubuntu24/ubuntu26), so match any of them
            return ["ubuntu", "x86_64"]
        elif "arm" in machine:
            # armhf/arm64 also depend on the SDK version
            return ["raspbian"]
        else:
            sys.exit("Your architecture is not supported")


def local_glibc_version():
    lib, version = platform.libc_ver()
    if lib != "glibc" or not version:
        return None
    return tuple(int(part) for part in version.split("."))


def build_runs_locally(filename):
    glibc = local_glibc_version()
    if glibc is None:
        return True
    for ubuntu_release, minimum in UBUNTU_GLIBC.items():
        if "ubuntu%s_" % ubuntu_release in filename:
            return glibc >= minimum
    return True


def find_sdk_file(scraper, version, tokens):
    r = scraper.get(url + "/" + version + "/")
    page = bs4.BeautifulSoup(r.text, features="html.parser")
    filenames = [
        a.get("href").split("/")[-1]
        for a in page.find_all("a")
        if a.get("href") and a.get("href").endswith(".7z")
    ]
    candidates = [f for f in filenames if not f.startswith("tt5prosdk")]
    matching = [f for f in candidates if all(token in f for token in tokens)]
    return next((f for f in matching if build_runs_locally(f)), None)


def download() -> None:
    scraper = cloudscraper.create_scraper()
    scraper.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    })
    r = scraper.get(url)
    page = bs4.BeautifulSoup(r.text, features="html.parser")

    # Get all <li> tags from the page
    versions = page.find_all("li")
    version_items = [i for i in versions if i.a and i.a.get("href").endswith("/")]
    if not version_items:
        sys.exit("No SDK versions found on the page.")

    # Try the stable 5.15 versions first, then the newest listed versions
    preferred = [i for i in version_items if "5.15" in i.text] or version_items[::-1]

    tokens = get_platform_tokens()
    version = sdk_file = None
    for item in preferred:
        candidate = item.a.get("href").strip("/")
        sdk_file = find_sdk_file(scraper, candidate, tokens)
        if sdk_file:
            version = candidate
            break
    if version is None:
        sys.exit("No compatible SDK download found for this platform.")

    print("Selected SDK version:", version)
    download_url = "/".join([url, version, sdk_file])

    print("Downloading from " + download_url)
    downloader.download_file(download_url, os.path.join(os.getcwd(), "ttsdk.7z"))


def extract() -> None:
    try:
        os.mkdir(os.path.join(os.getcwd(), "ttsdk"))
    except FileExistsError:
        shutil.rmtree(os.path.join(os.getcwd(), "ttsdk"))
        os.mkdir(os.path.join(os.getcwd(), "ttsdk"))
    patoolib.extract_archive(
        os.path.join(os.getcwd(), "ttsdk.7z"), outdir=os.path.join(os.getcwd(), "ttsdk")
    )


def move() -> None:
    path = os.path.join(os.getcwd(), "ttsdk", os.listdir(os.path.join(os.getcwd(), "ttsdk"))[0])
    libraries = ["TeamTalk_DLL", "TeamTalkPy"]
    dest_dir = os.path.join(os.getcwd(), os.pardir) if os.path.basename(os.getcwd()) == "tools" else os.getcwd()
    for library in libraries:
        try:
            os.rename(
                os.path.join(path, "Library", library), os.path.join(dest_dir, library)
            )
        except OSError:
            shutil.rmtree(os.path.join(dest_dir, library))
            os.rename(
                os.path.join(path, "Library", library), os.path.join(dest_dir, library)
            )
    try:
        os.rename(
            os.path.join(path, "License.txt"), os.path.join(dest_dir, "TTSDK_license.txt")
        )
    except FileExistsError:
        os.remove(os.path.join(dest_dir, "TTSDK_license.txt"))
        os.rename(
            os.path.join(path, "License.txt"), os.path.join(dest_dir, "TTSDK_license.txt")
        )


def clean() -> None:
    os.remove(os.path.join(os.getcwd(), "ttsdk.7z"))
    shutil.rmtree(os.path.join(os.getcwd(), "ttsdk"))


def install() -> None:
    print("Installing TeamTalk SDK components")
    print("Downloading latest SDK version...")
    download()
    print("Downloaded. Extracting...")
    extract()
    print("Extracted. Moving files...")
    move()
    print("Moved. Cleaning temporary files...")
    clean()
    print("Cleaned.")
    print("Installation complete.")


if __name__ == "__main__":
    install()
