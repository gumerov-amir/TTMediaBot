# TTMediaBot
A bot for music streaming to TeamTalk Servers.

## Installation and usage
### Requirements
* To use this bot you will need Python3 installed;
* You will need p7zip or p7zip-full on linux or 7zip on windows to install TeamTalk SDK;
* You will need pulseaudio and VLC installed on linux (there is no pulseaudio on Windows, so you need a virtual audio device driver such as VBCable for audio routing).
### Installation
* Download TTMediaBot;
* install all python requirements from requirements.txt with pip or pip3;
* Run ttsdk_downloader.py from tools folder;
* Copy or rename config_default.json to config.json;
* Fill in all required fields in config.json (Config description will be there later);
* On Linux run TTMediaBot.sh --devices to list all available devices and their numbers;
* On Windows run TTMediaBot.py --devices to list all available devices with their numbers;
* Edit config.json (change device numbers to appropriate for your purposes);
### Usage
* On Linux run ./TTMediaBot.sh;
* On Windows run python TTMediaBot.py directly.

## Startup options
* --devices - Shows list of all available input and output audio devices;
* -c PATH - Sets path to config file.

## Config file options
* language - Sets bot interface language. Warning! to select some language you need appropriate language folder inside "locale" folder;
* sound devices - Here you have to enter audio device numbers. Devices should be connected to each other (like Virtual audio cabble or pulseaudio);
* player - Here are some defaults about playback;
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

# contacts
E-mail - TTMediaBot@gmail.com
telegram channel: https://t.me/TTMediaBot_official
