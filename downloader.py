import requests

import shutil


def download_file(url: str, file_path: str) -> None:
    with requests.get(url, stream=True) as r:
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
