import sys

import vk_api
from vk_api import audio

def initialize_vk(config):
    vk_session = vk_api.VkApi(config["login"], config["password"])
    try:
        vk_session.auth()
    except Exception as e:
        sys.exit(e)
    vk_audio = audio.VkAudio(vk_session)
    return vk_audio
