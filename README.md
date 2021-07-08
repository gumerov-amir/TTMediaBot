# TTMediaBot
A bot for music streaming to TeamTalk Servers.

## Installation and usage
### Requirements
* To use the bot, you need to install Python on your computer;
* The bot requires the TeamTalk SDK component to be downloaded using the integrated tool from the command line. In order to download and extract the mentioned component, on Linux, you need to install p7zip or p7zip-full, or if you want to run the bot on Windows, 7Zip must be installed;
* If you are going to use Linux as your main system for a bot, you will need pulseaudio and libmpv  to route and play audio, but if you're planing to run a bot on Windows, PulseAudio is not available, so you will need a virtual audio cable driver, such as VBCable and of course, the mpv player library must also be installed. on Windows this library can be installed using an integrated tool.
### Installation
* Download TTMediaBot;
* install all python requirements from requirements.txt, using the "pip3 install -r requirements.txt" or just "pip install -r requirements.txt" command, without quotes;;
* Run ttsdk_downloader.py from the tools folder;
* If you're using Windows run libmpv_win_downloader.py from the tools folder;
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
# contacts
E-mail - TTMediaBot@gmail.com
telegram channel: https://t.me/TTMediaBot_official
