import shutil
from pathlib import Path

import requests


def download_file(url: str, file_path: str) -> None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    }
    with (
        requests.get(url, headers=headers, stream=True, timeout=60) as r,
        Path(file_path).open("wb") as f,
    ):
        shutil.copyfileobj(r.raw, f)
