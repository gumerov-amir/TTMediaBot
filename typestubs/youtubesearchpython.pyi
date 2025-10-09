from typing import Any

class VideosSearch:
    def __init__(
        self,
        query: str,
        limit: int = ...,
        language: str = ...,
        region: str = ...,
    ) -> None: ...
    def result(self, mode: int = ...) -> dict[str, Any]: ...
