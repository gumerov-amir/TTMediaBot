import inspect
import textwrap

import httpx
import youtubesearchpython.handlers.componenthandler as ch


def patch_httpx_post_proxies() -> None:
    """
    Ignore deprecated 'proxies' kwarg on httpx>=0.28 used by youtubesearchpython.
    """
    if "proxies" in inspect.signature(httpx.post).parameters:
        return
    original_post = httpx.post

    def _post(*args, **kwargs):
        kwargs.pop("proxies", None)
        return original_post(*args, **kwargs)

    httpx.post = _post


def patch_channel_link_none() -> None:
    """
    Prevent TypeError when channel id is None in youtubesearchpython.
    """
    src = inspect.getsource(ch.ComponentHandler._getVideoComponent)
    needle = "component['channel']['link'] = 'https://www.youtube.com/channel/' + component['channel']['id']"
    if needle not in src:
        return
    patched = src.replace(
        needle,
        "channel_id = component.get('channel', {}).get('id')\n"
        "        component['channel']['link'] = "
        "('https://www.youtube.com/channel/' + channel_id) if channel_id else None",
    )
    ns = {}
    exec(textwrap.dedent(patched), ch.__dict__, ns)
    ch.ComponentHandler._getVideoComponent = ns["_getVideoComponent"]
