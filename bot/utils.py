from pathlib import Path

from bot import app_vars


def clean_file_name(file_name: str) -> str:
    for char in ["\\", "/", "%", "*", "?", ":", '"', "|"] + [
        chr(i) for i in range(1, 32)
    ]:
        file_name = file_name.replace(char, "_")
    return file_name.strip()


def get_abs_path(file_name: str) -> str:
    return str(Path(app_vars.directory) / file_name)
