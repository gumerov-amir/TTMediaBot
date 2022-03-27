from __future__ import annotations
from typing import Any, Dict, Optional

class YoutubeDL:
    def __init__(
        self, params: Optional[Dict[str, Any]] = ..., auto_init: bool = ...
    ) -> None: ...
    def __enter__(self) -> YoutubeDL: ...
    def __exit__(self) -> None: ...
    def extract_info(
        self,
        url: Optional[str],
        download: bool = ...,
        ie_key: Optional[str] = ...,
        extra_info: Optional[Dict[str, Any]] = ...,
        process: bool = ...,
        force_generic_extractor: bool = ...,
    ) -> Dict[str, Any]: ...
    def process_ie_result(
        self,
        ie_result: Dict[str, Any],
        download: bool = ...,
        extra_info: Optional[Dict[str, Any]] = ...,
    ) -> Dict[str, Any]: ...
