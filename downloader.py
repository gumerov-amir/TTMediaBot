import shutil

import requests


def download_file(url: str, file_path: str) -> None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"
    }
    with requests.get(url, headers=headers, stream=True) as r:
        try:
            with open(file_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        except Exception as e:
            print(f"An error occurred while downloading the file: {e}")
