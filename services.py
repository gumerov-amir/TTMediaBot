import requests
import vk_api
from vk_api import audio

def initialize_vk(config):
    http = requests.Session()
    http.headers.update({
    "User-agent": "KateMobileAndroid/47-427 (Android 6.0.1; SDK 23; armeabi-v7a; samsung SM-G900F; ru)"
    })
    vk_session = vk_api.VkApi(login=config["login"], password=config["password"], token=config["token"], session=http)
    #try:
        # vk_session.auth()
    # except Exception as e:
        # sys.exit(e)
    # vk_audio = audio.VkAudio(vk_session)
    return vk_session.get_api()
