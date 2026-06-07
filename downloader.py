import requests
import shutil

def download_file(url: str, file_path: str, headers: dict[str, str] = {}) -> None:
    with requests.get(url, headers=headers, stream=True) as r:
        try:
            with open(file_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        except Exception as e:
            print(f"An error occurred while downloading the file: {e}")
