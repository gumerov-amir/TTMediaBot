# TTMediaBot
A media streaming bot for TeamTalk.

## Installation and usage
### Requirements
* To use the bot, you need to install Python 3.7 or later;
* The bot requires the TeamTalk SDK component to be downloaded using the integrated tool from the command line. In order to download and extract the mentioned component, on Linux, you need to install p7zip or p7zip-full, or if you want to run the bot on Windows, 7Zip must be installed;
* If you are going to use Linux as your main system for a bot, you will need pulseaudio and libmpv  to route and play audio, but if you re using Windows, PulseAudio is not available, so you will need a virtual audio cable driver, such as VBCable and of course, the mpv player library must also be installed. on Windows this library can be installed using an integrated tool. On Debian-based systems the required package is libmpv1.

### Installation
* Download TTMediaBot;
* install all python requirements from requirements.txt, using the "pip3 install -r requirements.txt" or just "pip install -r requirements.txt" command, without quotes;;
* Run ttsdk_downloader.py from the tools folder;
* If you're using Windows run libmpv_win_downloader.py from the tools folder;
* Copy or rename config_default.json to config.json;
* Fill in all required fields in config.json (Config description will be there later);
* On Linux run TTMediaBot.sh --devices to list all available devices and their numbers;
* On Windows run TTMediaBot.py --devices to list all available devices with their numbers;
* Edit config.json (change device numbers appropriately for your purposes);

### Usage
* On Linux run ./TTMediaBot.sh;
* On Windows run python TTMediaBot.py directly.

### Running in Docker
You can also run the bot in a Docker container.
First of all, You should build an image from the provided Dockerfile:
```sh
docker build -t ttmediabot .
```
Note: The first run could take some time.

Then you can run the Docker container with the following command:
```sh
docker run --rm --name ttmb_1 -dv <path/to/data/directory>:/home/ttbot/data ttmediabot
```
<path/to/data/directory> here means a directory where config.json file will be stored. It should not contain any other unrelated data.
The cache and  log files will be stored in the specified directory.

## Startup options
* --devices - Shows the list of all available input and output audio devices;
* -c PATH - Sets the path to the configuration file.

## Config file options
* language - Sets the bot's interface language. Warning! to select a language you need an appropriate language folder inside the "locale" folder;
* sound devices - Here you have to enter audio device numbers. Devices should be connected to each other (like Virtual audio cable or pulseaudio);
* player - This section sets the configuration for the player such as default volume, maximum volume, etc;
* teamtalk - here are main options for bot to connect and login to your TeamTalk server;
* Services - Here you should configure available services for music search and playback;
* logger - Here you can configure various logging related options.

## Pulse audio or VB cable settings
### Linux variant
* Install pulseaudio.
* type $pulseaudio --start
* Next command creates null sink and this sink can be monitored by default pulse input device.
$pacmd load-module module-null-sink
* then run ./TTMediaBot.sh --devices and check its numbers.
output should be null audio output, input should be pulse.
* put this numbers to your config.json.

### windows variant
* install VB-cable, run "TTMediaBot.py --devices" and check numbers of VB-cable devices
* put this numbers to your config.json.

## Some notes about the Windows variant
* When listing input and output devices in the Windows variant of TTMediaBot, please note, that the input device will be doubled, i.e., if the output device is line 1 with number 3, the input device for line 1 will be listed twice, at number 5 and, for example, at number 7.
* The correct number will be the last one as input, that is, if we selected the output as line 1 with the number 3, the input device would be line 1 with number 7 of the two options, number 5 and number 7.
* The same method applies to all numbers and all Input / Outputs.

note also that you don't have to downgrade surten libraries like httpx, instead if you aren't on a proxy you can patch httpx and request/related instead.

1: change the following script in "C:\Users\yourusername\AppData\Local\Programs\Python\Python312\Lib\site-packages\requestsreurn httpx.post(self.url, headers=self.headers, data=self.data, proxies=self.proxies)
to:
return httpx.post(self.url, headers=self.headers, data=self.data)
2. Save the file.
Step 2: Clear Python Cache
• Remove cached files to ensure the patch takes effect:
rmdir /s /q C:\Users\HP\AppData\Local\Programs\Python\Python312\Lib\site-packages\youtubesearchpython\__pycache__
rmdir /s /q filepath\TTMediaBot-master\__pycache__
Step 3: Verify config.json
• Ensure config.json is set to avoid proxies:
"player": {
    "default_volume": 50,
    "max_volume": 100,
    "volume_fading": true,
    "volume_fading_interval": 0.025,
    "seek_step": 5,
    "youtube_cookies_file": "",
    "player_options": {
        "noproxy": "*"
        
        # support us
* yoomoney: https://yoomoney.ru/to/4100117354062028

# contacts
* telegram channel: https://t.me/TTMediaBot_chat
* E-mail: TTMediaBot@gmail.com
