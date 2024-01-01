import gettext
from pathlib import Path
from typing import List

from bot import app_vars, errors


class Translator:
    def __init__(self, language: str) -> None:
        self._locale = "en"
        self.set_locale(language)

    def get_locale(self) -> str:
        return self._locale

    def get_locales(self) -> List[str]:
        return ["en"] + [entry.name for entry in Path(app_vars.directory, "locale").iterdir() if entry.is_dir()]

    def set_locale(self, locale: str) -> None:
        if locale in self.get_locales() or locale == "en":
            self._locale = locale
            self.translation = gettext.translation(
                "TTMediaBot",
                str(Path(app_vars.directory) / "locale"),
                languages=[locale],
                fallback=True,
            )
        else:
            raise errors.LocaleNotFoundError()

    def translate(self, message: str) -> str:
        return self.translation.gettext(message)
