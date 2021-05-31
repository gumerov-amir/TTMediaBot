import gettext
import os

from bot import vars


def install_locale(language, fallback=True):
    translation = gettext.translation('TTMediaBot', os.path.join(vars.directory, 'locale'), languages=[language], fallback=fallback)
    translation.install()

def get_locales():
    return ['en'] + os.listdir(os.path.join(vars.directory, 'locale'))
