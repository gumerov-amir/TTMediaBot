import gettext
import os

from bot import vars


def install_locale(language):
    translation = gettext.translation('TTMediaBot', os.path.join(vars.directory, 'locale'), languages=[language], fallback=True)
    translation.install()


