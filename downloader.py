import requests
import shutil

def download_file(url: str, file_path: str) -> None:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    with requests.get(url, headers=headers, stream=True) as r:
        try:
            with open(file_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        except Exception as e:
            print(f"An error occurred while downloading the file: {e}")
