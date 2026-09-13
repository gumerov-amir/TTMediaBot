#!/usr/bin/env python3

import os
import platform
import re
import shutil
import sys
from urllib.parse import urljoin

import bs4
import patoolib
import requests

path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
url = "https://bearware.dk/teamtalksdk/"
headers = {
    "User-Agent": "TTMediaBot SDK downloader/1.0",
}


def get_url_suffix_from_platform() -> str:
    machine = platform.machine().lower()

    if sys.platform == "win32":
        if platform.architecture()[0] == "64bit" and machine in {
            "amd64",
            "x86_64",
        }:
            return "win64"
        sys.exit("Only 64-bit x86 Windows is supported")

    if sys.platform == "darwin":
        if machine in {"arm64", "x86_64"}:
            return "macos_universal"
        sys.exit("Your macOS architecture is not supported")

    if sys.platform.startswith("linux"):
        if machine in {"amd64", "x86_64"}:
            return "ubuntu22_x86_64"
        if machine in {"aarch64", "arm64"}:
            return "raspbian_arm64"

    sys.exit("Your platform or architecture is not supported")


def _get_page(page_url: str) -> str:
    response = requests.get(page_url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def _version_key(version: str) -> tuple:
    match = re.fullmatch(r"v(\d+)\.(\d+)(?:\.(\d+))?([a-z]*)", version)
    if match is None:
        return ()
    return (
        int(match.group(1)),
        int(match.group(2)),
        int(match.group(3) or -1),
        match.group(4),
    )


def get_download_url() -> str:
    page = bs4.BeautifulSoup(_get_page(url), features="html.parser")
    versions = {
        anchor.get("href", "").rstrip("/")
        for anchor in page.find_all("a", href=True)
    }
    versions = [version for version in versions if _version_key(version)]
    if not versions:
        raise RuntimeError("No TeamTalk SDK releases were found")

    version = max(versions, key=_version_key)
    version_url = urljoin(url, f"{version}/")
    filename = f"tt5sdk_{version}_{get_url_suffix_from_platform()}.7z"
    version_page = bs4.BeautifulSoup(
        _get_page(version_url),
        features="html.parser",
    )
    archive_links = {
        anchor.get("href", "")
        for anchor in version_page.find_all("a", href=True)
    }
    if filename not in archive_links:
        raise RuntimeError(
            f"TeamTalk SDK {version} is not available for this platform"
        )

    return urljoin(version_url, filename)


def download() -> None:
    download_url = get_download_url()
    print(f"Downloading from {download_url}")
    archive = os.path.join(path, "ttsdk.7z")
    temporary_archive = f"{archive}.part"
    try:
        with requests.get(
            download_url,
            headers=headers,
            stream=True,
            timeout=60,
        ) as response:
            response.raise_for_status()
            with open(temporary_archive, "wb") as archive_file:
                shutil.copyfileobj(response.raw, archive_file)
        os.replace(temporary_archive, archive)
    finally:
        if os.path.exists(temporary_archive):
            os.remove(temporary_archive)


def extract() -> None:
    extract_dir = os.path.join(path, "ttsdk")
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.mkdir(extract_dir)
    patoolib.extract_archive(
        os.path.join(path, "ttsdk.7z"),
        outdir=extract_dir,
    )


def _find_sdk_root(extract_dir: str) -> str:
    for root, directories, _ in os.walk(extract_dir):
        if "Library" not in directories:
            continue
        library_dir = os.path.join(root, "Library")
        if all(
            os.path.isdir(os.path.join(library_dir, library))
            for library in ("TeamTalk_DLL", "TeamTalkPy")
        ) and os.path.isfile(os.path.join(root, "License.txt")):
            return root
    raise RuntimeError("The downloaded archive has an unexpected layout")


def _remove_existing(target: str) -> None:
    if os.path.isdir(target) and not os.path.islink(target):
        shutil.rmtree(target)
    elif os.path.lexists(target):
        os.remove(target)


def move() -> None:
    sdk_root = _find_sdk_root(os.path.join(path, "ttsdk"))
    for library in ("TeamTalk_DLL", "TeamTalkPy"):
        source = os.path.join(sdk_root, "Library", library)
        destination = os.path.join(path, library)
        _remove_existing(destination)
        shutil.move(source, destination)

    source = os.path.join(sdk_root, "License.txt")
    destination = os.path.join(path, "TTSDK_license.txt")
    _remove_existing(destination)
    shutil.move(source, destination)


def clean() -> None:
    for archive in ("ttsdk.7z", "ttsdk.7z.part"):
        archive_path = os.path.join(path, archive)
        if os.path.exists(archive_path):
            os.remove(archive_path)
    shutil.rmtree(os.path.join(path, "ttsdk"), ignore_errors=True)


def install() -> None:
    print("Installing TeamTalk SDK components")
    try:
        download()
        extract()
        move()
    finally:
        clean()
    print("Installed, exiting.")


if __name__ == "__main__":
    install()
