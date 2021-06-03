#!/usr/bin/env python3

import os
import sys
import subprocess


path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'locale')

def main():
    if sys.platform == 'win32':
        msgfmt_path = '"{exec}" "{file}"'.format(exec=sys.executable, file=os.path.join(os.path.dirname(sys.executable), 'Tools', 'i18n', 'msgfmt.py'))
    else:
        msgfmt_path = 'msgfmt'
    for i in os.listdir(path):
        code = subprocess.call('{msgfmt_path} -o "{mo}" "{po}"'.format(msgfmt_path=msgfmt_path, po=os.path.join(path, i, 'LC_MESSAGES', 'TTMediaBot.po'), mo=os.path.join(path, i, 'LC_MESSAGES', 'TTMediaBot.mo')), shell=True)
        if code != 0:
            print('Gettext is not installed on your computer.\nplease, installed it for using bot')
            break


if __name__ == '__main__':
    main()

