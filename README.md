# TTMediaBot
A bot for music streaming to TeamTalk Servers.

## Installation and usage
### Requirements
* To use the bot, you need to have Python 3.7 or higher on your computer.
* The bot requires the TeamTalk SDK component to be downloaded using the integrated tool, which can be run from the command line. In order to download and extract the mentioned component, on Linux, you need to install p7zip or p7zip-full, or if you want to run the bot on Windows, 7Zip must be installed;
* If you are going to use Linux as your main system for a bot, you will need pulseaudio and libmpv  to route and play audio. But if you're using Windows, PulseAudio is not available, so you will need a virtual audio cable driver, such as VBCable. You will also need to have the mpv player library  installed. on Windows this library can be installed using an integrated tool. On Debian-based systems the required package is libmpv1.
### Installation
* Download TTMediaBot.
* install all python requirements from the requirements.txt file, by executing pip3 install -r requirements.txt on a Linux system. On Windows systems, execute pip install -r requirements.txt. Note: if you're running the pip3 command on a Linux system and you get an error saying command not found or something similar, ensure that the python3-pip package is installed. On Ubuntu, this can be done by running sudo apt install python3-pip.
* Run ttsdk_downloader.py from the tools folder.
* If you're using Windows, run libmpv_win_downloader.py from the tools folder;
* Copy or rename config_default.json to config.json. On Linux, this can be done by executing cp config_default.json config.json. However, make sure you're in the TTMediaBot directory with the pwd command first.
* Fill in all required fields in config.json. Detailed instructions on how to do this are located further on in this documentation.
* On Linux, run TTMediaBot.sh --devices from the TTMediaBot directory to list all available devices and their corresponding numbers.
* On Windows, run TTMediaBot.py --devices from the TTMediaBot directory to list all available devices with their corresponding numbers.
### Usage
* To start the TT media bot on Linux, from the TTMediaBot directory, run ./TTMediaBot.sh.
* To start the TT media bot on Windows, run python TTMediaBot.py.
### Running in Docker
You can also run the bot from inside a Docker container.
First of all, You will need to build an image from the provided Dockerfile:
```sh
docker build -t ttmediabot .
```
Note: The first run could take some time.

Then you can run the Docker container with the following command:
```sh
docker run --rm --name ttmb_1 -dv <path/to/data/directory>:/home/ttbot/data ttmediabot
```
<path/to/data/directory> here means a directory where the config.json file will be stored. It should not contain any other unrelated data.
The cache and  log files will be stored in the specified directory.

## Startup options
* --devices - Shows the list of all available input and output audio devices.
* -c PATH - Sets the path to the configuration file.

## Config file options
* language. Sets the bot's interface language. Warning! to select a language you need an appropriate language folder inside the "locale" folder.
* sound devices. Here you have to enter audio device numbers. Devices should be connected to each other (like Virtual audio cable or pulseaudio).
* player. This section sets the configuration for the player such as default volume, maximum volume, etc.
* teamtalk. This section defines the parameters for allowing the bot to connect and log into your TeamTalk server. Hostname, ports, encryption mode etc.
* Services. Here you can configure available services for music search and playback.
* logger. Here you can configure various options regarding data stored in the bot's log files.

## Pulse audio or VB cable settings
### Linux variant
* Install pulseaudio.
* type $pulseaudio --start.
* create the null sink, which will be monitored by the default pulseaudio input device.
$pacmd load-module module-null-sink
* Run ./TTMediaBot.sh --devices and review its output to see the numbers associated with each audio device listed.
The output device should be null output, and the input device should be pulse.
* Open the config.json file in a text editor, navigate to the sound devices section and change the numbers in the input and output device fields to match those corresponding to the aforementioned input and output devices.
### windows variant
* install VB-cable.
* Run TTMediaBot.py --devices from the command prompt and check the associated numbers of your VB-cable devices
* Open the config.json file in a text editor, navigate to the sound devices section and change the numbers in the input and output devices field accordingly.
## Some notes about the Windows variant
* When listing input and output devices in the Windows variant of TTMediaBot, please note, that the input device will be doubled, i.e., if the output device is line 1 with number 3, the input device for line 1 will be listed twice, at number 5 and, for example, at number 7.
* The correct number will be the last one as input, that is, if we selected the output as line 1 with the number 3, the input device would be line 1 with number 7 of the two options, number 5 and number 7.
* The same method applies to all numbers and all Input / Outputs.
## support us
* yoomoney: https://yoomoney.ru/to/4100117354062028
## contacts
* telegram channel: https://t.me/TTMediaBot_chat
* Email: TTMediaBot@gmail.com
