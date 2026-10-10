import requests
import shutil

def download_file(url: str, file_path: str) -> None:
    headers = {
        "User-Agent": "curl/8.1.2",
        "Accept": "*/*",
    }
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        try:
            with open(file_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        except Exception as e:
            print(f"An error occurred while downloading the file: {e}")
            raise
