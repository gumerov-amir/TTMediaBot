from typing import Any

import requests


class Audio:
    def get(
        self,
        owner_id: int = 1,
        album_id: int = 1,
        count: int = ...,
    ) -> dict[str, Any]: ...

    def search(
        self,
        q: str = "",
        count: int = 100,
        sort: int = 0,
    ) -> dict[str, Any]: ...


class Account:
    def getInfo(self) -> dict[str, Any]: ...  # noqa: N802


class Utils:
    def resolveScreenName(self, screen_name: str = "") -> dict[str, Any]: ...  # noqa: N802


class Api:
    account: Account
    audio: Audio
    utils: Utils


class VkApi:
    def __init__(
        self,
        token: str = "",
        session: requests.Session = ...,
        api_version: str = "",
    ) -> None: ...

    def get_api(self) -> Api: ...
