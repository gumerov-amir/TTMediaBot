import os
import platform
import shutil
import sys
from urllib import request

import py7zr

import bs4


url = 'http://bearware.dk/teamtalksdk'
user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'

cd = os.path.dirname(os.path.abspath(__file__))


def get_url_suffix_from_platform():
    if sys.platform == 'win32':
        if platform.machine()[0:3] == 'AMD':
            if platform.architecture()[0][0:2] == '64':
                return 'win64'
            else:
                return 'win32'
        else:
            sys.exit('Your system is not supported.')
    elif sys.platform == 'darwin':
        sys.exit('Your platform is not supported.')
    else:
        if platform.machine()[0:2] == 'AMD':
            return 'debian9_x86_64'
        else:
            return 'raspbian_armhf'

def download():
    r = request.urlopen(url)
    html = r.read().decode('UTF-8')
    page = bs4.BeautifulSoup(html)
    versions = page.find_all('li')
    last_version = versions[-1].a.get('href')[0:-1]
    download_url = url + '/' + last_version + '/' + 'tt5sdk_{v}_{p}.7z'.format(v=last_version, p=get_url_suffix_from_platform())
    print(download_url)
    request.urlretrieve(download_url, os.path.join(cd, 'ttsdk.7z'))

def extract():
    py7zr.unpack_7zarchive(os.path.join(cd, 'ttsdk.7z'), os.path.join(cd, 'ttsdk'))

def move():
    path = os.path.join(cd, 'ttsdk', os.listdir(os.path.join(cd, 'ttsdk'))[0])
    if sys.platform == 'win32':
        shutil.move(os.path.join(path, 'Library/TeamTalk_DLL/TeamTalk5.dll'), os.path.join(cd, 'TeamTalk5.dll'))
    else:
        shutil.move(os.path.join(path, 'Library/TeamTalk_DLL/libTeamTalk5.so'), os.path.join(cd, 'libTeamTalk5.so'))
    shutil.move(os.path.join(path, 'Library/TeamTalkPy'), os.path.join(cd, 'TeamTalkPy'))

def clean():
    os.remove('ttsdk.7z')
    shutil.rmtree('ttsdk')

def install():
    download()
    extract()
    move()
    clean()

if __name__ == "__main__":
    install()
