#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

cd = Path(__file__).resolve().parent.parent
locale_path = cd / "locale"
pot_file_path = locale_path / "TTMediaBot.pot"
source_paths = [str(cd / "bot"), str(cd / "TTMediaBot.py")]
babel_prefix = f"{sys.executable} -m babel.messages.frontend"
locale_domain = "TTMediaBot"


def extract() -> None:
    code = subprocess.call(  # noqa: S602
        f"{babel_prefix} extract {' '.join(source_paths)} -o {pot_file_path} --keywords=translate -c translators: --copyright-holder=TTMediaBot-team --project=TTMediaBot",
        shell=True,
    )
    if code:
        sys.exit("Bable is not installed. please install all the requirements")


def update() -> None:
    code = subprocess.call(  # noqa: S602
        f"{babel_prefix} update -i {pot_file_path} -d {locale_path} -D {locale_domain} --update-header-comment --previous",
        shell=True,
    )
    if code:
        sys.exit(code)


def compile_locales() -> None:
    code = subprocess.call(  # noqa: S602
        f"{babel_prefix} compile -d {locale_path} -D {locale_domain}",
        shell=True,
    )
    if code:
        sys.exit(code)


def main() -> None:
    extract()
    update()
    compile_locales()


if __name__ == "__main__":
    main()
