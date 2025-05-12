from __future__ import annotations

from typing import Any

from typing_extensions import Self

class YoutubeDL:
    def __init__(
        self,
        params: dict[str, Any] | None = ...,
        auto_init: bool = ...,
    ) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self) -> None: ...
    def extract_info(
        self,
        url: str | None,
        download: bool = ...,
        ie_key: str | None = ...,
        extra_info: dict[str, Any] | None = ...,
        process: bool = ...,
        force_generic_extractor: bool = ...,
    ) -> dict[str, Any]: ...
    def process_ie_result(
        self,
        ie_result: dict[str, Any],
        download: bool = ...,
        extra_info: dict[str, Any] | None = ...,
    ) -> dict[str, Any]: ...
