import os

from bot import vars

def check_file_path(file_name):
        if os.path.isfile(file_name):
            return True
        elif os.path.isfile(os.path.join(vars.directory, file_name)):
            return True
        else:
            return False
