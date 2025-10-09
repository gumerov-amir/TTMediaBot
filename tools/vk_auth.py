#!/usr/bin/env python3

import json
from getpass import getpass

import requests


class AuthenticationError(Exception):
    pass


class PhoneValidationError(Exception):
    pass


class TokenValidationError(Exception):
    pass


client_id = "2274003"
client_secret = "hHbZxrka2uZ6jB1inYsH"
api_ver = "5.89"
scope = "all"
user_agent = "VKAndroidApp/6.2-5091 (Android 9; SDK 28; samsungexynos7870; samsung j6lte; 720x1450)"
api_url = "https://api.vk.com/method/"
receipt = "fkdoOMX_yqQ:APA91bHbLn41RMJmAbuFjqLg5K-QW7si9KajBGCDJxcpzbuvEcPIk9rwx5HWa1yo1pTzpaKL50mXiWvtqApBzymO2sRKlyRiWqqzjMTXUyA5HnRJZyXWWGPX8GkFxQQ4bLrDCcnb93pn"


def request_auth(login: str, password: str, scope: str = "", code: str = "") -> str:
    if not (login or password):
        raise ValueError
    url = (
        "https://oauth.vk.com/token?grant_type=password&client_id="
        + client_id
        + "&client_secret="
        + client_secret
        + "&username="
        + login
        + "&password="
        + password
        + "&v="
        + api_ver
        + "&2fa_supported=1&force_sms=1"
    )
    if scope:
        url += "&scope=" + scope
    if code:
        url += "&code=" + code
    headers = {"User-Agent": user_agent}
    r = requests.get(url, headers=headers)
    if r.status_code == 200 and "access_token" in r.text:
        res = r.json()
        return res["access_token"]
    if "need_validation" in r.text:
        res = r.json()
        sid = res["validation_sid"]
        code = handle_2fa(sid)
        return request_auth(login, password, scope=scope, code=code)
    raise AuthenticationError(r.text)


def handle_2fa(sid: str) -> str:
    if not sid:
        msg = "No sid is given"
        raise ValueError(msg)
    url = api_url + "auth.validatePhone?sid=" + sid + "&v=" + api_ver
    headers = {"User-Agent": user_agent}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        code = ""
        while not code:
            code = input("SMS code: ")
            if len(code) != 6 or not code.isdigit():
                continue
            return code
        return None
    raise PhoneValidationError(r.text)


def validate_token(token: str) -> str:
    if not (token):
        msg = "Required argument is missing"
        raise ValueError(msg)
    url = (
        api_url
        + "auth.refreshToken?access_token="
        + token
        + "&receipt="
        + receipt
        + "&v="
        + api_ver
    )
    headers = {"User-Agent": user_agent}
    r = requests.get(url, headers=headers)
    if r.status_code == 200 and "token" in r.text:
        res = r.json()
        received_token = res["response"]["token"]
        if not received_token:
            raise TokenValidationError(r.text)
        return received_token
    raise TokenValidationError(r.text)


def main() -> None:
    login = ""
    password = ""
    try:
        while not login:
            login = input("Phone, email or  login: ")
        while not password:
            password = getpass("Password: ")
        token = request_auth(login, password, scope=scope)
        validated_token = validate_token(token)
        y_or_n = input("Do you want to save the token to the configuration file? y/n")
        if y_or_n == "y":
            config_file = input("Configuration file path: ")
            with open(config_file) as f:
                data = json.load(f)
            data["services"]["vk"]["token"] = validated_token
            with open(config_file, "w") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        else:
            pass
    except Exception:
        pass
    input("Press enter to continue")


if __name__ == "__main__":
    main()
