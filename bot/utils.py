import os

from bot import app_vars

def check_file_path(file_name):
        if os.path.isfile(file_name):
            return True
        elif os.path.isfile(os.path.join(app_vars.directory, file_name)):
            return True
        else:
            return False

def clean_file_name(file_name):
    for char in ["\\", "/", "%", "*", "?", ":", "\"", "|"] + [chr(i) for i in range(1,32)]:
        file_name = file_name.replace(char, "_")
    file_name = file_name.strip()
    return file_name

def get_abs_path(file_name):
    return os.path.join(app_vars.directory, file_name)




