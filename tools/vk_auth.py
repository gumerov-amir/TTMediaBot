#!/usr/bin/env python3

from getpass import getpass
from vkpymusic import TokenReceiver


class AuthenticationError(Exception):
    pass


class PhoneValidationError(Exception):
    pass


class TokenValidationError(Exception):
    pass


def on_2fa_handler() -> str:
    """Callback handler for two-factor authentication requested by vkpymusic."""
    print("Two factor authentication is required")
    code = ""
    while not code:
        code = input("SMS code: ")
        if len(code) != 6 or not code.isdigit():
            print("SMS code must be a string of 6 digits")
            continue
        return code


def on_captcha_handler(captcha_url: str) -> str:
    """Callback handler for captcha resolution requested by vkpymusic."""
    print(f"Captcha validation required. URL: {captcha_url}")
    return input("Captcha code: ").strip()


def main():
    login = ""
    password = ""
    try:
        print("VK Authentication Helper for TTMediaBot")
        print()
        print("Enter your VK credentials to continue")
        while not login:
            login = input("Phone, email or  login: ")
        while not password:
            password = getpass("Password: ")
        
        # Initializing the vkpymusic token receiver with credentials
        receiver = TokenReceiver(login=login, password=password)
        
        # Performing authentication via vkpymusic built-in method
        if not receiver.auth(on_2fa=on_2fa_handler, on_captcha=on_captcha_handler):
            raise AuthenticationError("vkpymusic authentication failed")
            
        validated_token = receiver.get_token()
        if not validated_token:
            raise TokenValidationError("Failed to extract token from session")

        y_or_n = input("Do you want to save the token to the configuration file? y/n")
        if y_or_n == "y":
            config_file = input("Configuration file path: ")
            
            # Using standard file reading without importing json module directly
            with open(config_file, "r", encoding="utf-8") as f:
                import json
                data = json.load(f)
                
            data["services"]["vk"]["token"] = validated_token
            
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
            print("Your token has been successfully saved to the configuration file")
        else:
            print("Your VK token:")
            print(validated_token)
    except Exception as e:
        print(e)
    input("Press enter to continue")


if __name__ == "__main__":
    main()
