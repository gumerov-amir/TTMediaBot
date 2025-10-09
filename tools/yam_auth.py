#!/usr/bin/env python3

import json
from getpass import getpass

import requests

CLIENT_ID = "23cabbbdc6cd418abb4b39c32c41195d"
CLIENT_SECRET = "53bc75238f0c4d08a118e51fe9203300"
USER_AGENT = "Yandex-Music-API"
HEADERS = {
    "X-Yandex-Music-Client": "YandexMusicAndroid/23020251",
    "USER_AGENT": USER_AGENT,
}
url = "https://oauth.yandex.ru/token"


def get_token(
    username,
    password,
    grant_type="password",
    x_captcha_answer=None,
    x_captcha_key=None,
):
    data = {
        "grant_type": grant_type,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "username": username,
        "password": password,
    }
    if x_captcha_answer and x_captcha_key:
        data.update({
            "x_captcha_answer": x_captcha_answer,
            "x_captcha_key": x_captcha_key,
        })
    try:
        resp = requests.request("post", url, data=data, headers=HEADERS)
    except requests.RequestException as e:
        raise NetworkError(e)
    if not (200 <= resp.status_code <= 299):
        msg = "Error"
        raise SystemError(msg)
    json_data = json.loads(resp.content.decode("utf-8"))
    return json_data["access_token"]


def main() -> None:
    login = ""
    password = ""
    try:
        while not login:
            login = input("email or  login: ")
        while not password:
            password = getpass("Password: ")
        token = get_token(login, password)
        y_or_n = input("Do you want to save the token to the configuration file? y/n")
        if y_or_n == "y":
            config_file = input("Configuration file path: ")
            with open(config_file) as f:
                data = json.load(f)
            try:
                data["services"]["yam"]["token"] = token
            except KeyError:
                data["services"]["yam"] = {"enabled": True, "token": token}
            with open(config_file, "w") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        else:
            pass
    except Exception:
        pass
    input("Press enter to continue")


if __name__ == "__main__":
    main()
