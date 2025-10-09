# TTMediaBot

A media streaming bot for TeamTalk.

Supports playing of music from VK, Yandex Music, Youtube, as well as playing any URLs supported by [yt-dlp](https://github.com/yt-dlp/yt-dlp) or [mpv](https://github.com/mpv-player/mpv).

## Installation and usage

### Requirements

* To use the bot, you need to install Python 3.10 or later;
* The bot requires the TeamTalk SDK component to be downloaded using the integrated tool from the command line. In order to download and extract the mentioned component, on Linux, you need to install p7zip, p7zip-full, or 7z, or if you want to run the bot on Windows, 7Zip must be installed and available via command line;
* To correctly process and route audio you will need pulseaudio or snd_aloop on Linux, some kind of virtual audio cable on Windows, as well as mpv player installed. To download and extract mpv on Windows use the corresponding tool in tools directory. On Linux just install libmpv1 package.

### Installation

* Download TTMediaBot;
* install all python requirements from requirements.txt, using the "pip3 install -r requirements.txt" or just "pip install -r requirements.txt" command, without quotes;;
* Run ttsdk_downloader.py from the tools folder;
* If you're using Windows run libmpv_win_downloader.py from the tools folder;
* Copy or rename config_default.json to config.json;
* Fill in all required fields in config.json (Config descriptions are provided in the comments);
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

### Installation with uv

You can install all dependencies and run the bot with uv python package manager.

Just use the usual uv commands as with any other project.

## Startup options

* `--devices` - Shows the list of all available input and output audio devices;
* `-c PATH` - Sets the path to the configuration file;
* `-l PATH` - Sets path to the log file;
* `--cache PATH` - Sets the path to the bot cache file;
* `--help` - Outputs command line usage help. Please first refer to this output as it is updated from the code.

## Pulse audio or VB cable settings

### Linux variant

* Install pulseaudio.
* type `pulseaudio --start`
* Next command creates null sink and this sink can be monitored by default pulse input device.
`pacmd load-module module-null-sink`
* then run `./TTMediaBot.sh --devices` and check its numbers.
output should be null audio output, input should be pulse.
* put this numbers to your config.json.

### windows variant

* install VB-cable, run `TTMediaBot.py --devices` and check numbers of VB-cable devices
* put this numbers to your config.json.

## Some notes about the Windows variant

* When listing input and output devices in the Windows variant of TTMediaBot, please note, that the input device will be doubled, i.e., if the output device is line 1 with number 3, the input device for line 1 will be listed twice, at number 5 and, for example, at number 7.
* The correct number will be the last one as input, that is, if we selected the output as line 1 with the number 3, the input device would be line 1 with number 7 of the two options, number 5 and number 7.
* The same method applies to all numbers and all Input / Outputs.

## Troubleshooting and caveats

### Bot fails at searching anything on Youtube with error about proxy

Install httpx version 0.27.0 with the following command: `pip install httpx==0.27.0`.
This is already listed in updated requirements.

### With snd_aloop bot outputs no sound at all

Now the list of input and output devices is a bit messy (this will be probably fixed later).
You need to experiment with different input and output device combinations to find the correct one.

Tip: do not touch any surround, 5.1, 7.1 and other strange device variants. Stick to default and loopback devices.

### Bot outputs a bunch of alsa error messages on every start

This is some kind of TeamTalk sdk bug and we cannot fix it at the moment.
Even with these errors the bot will work normally. This is **not** a cause of any possible errors.

### There are almost no input devices listed with `--devices` command

This is a known bug with alsa support of TeamTalk sdk version 5.15. Please, download and put the libTeamTalk5.so library from sdk version 5.14.

### Bot cannot play Youtube videos with errors about bots and signing in

Now the bot includes a support of cookie files. Please, read about how to get them from your browser on the yt-dlp github page.
The configuration file now contains a `cookiefile_path` option which allows to specify a path to the cookies file.

### Bot eats CPU and RAM quickly

We don't know the exact cause of this bug but it seems like this only happens when you use pulseaudio as your audio router and specify devices 0 and 0 in the configuration.

# Contributing

We are always glad to accept any cool pull requests, feature requests and bug reports.

When working on the code base, please don't ignore the formatter and linter requirements. Keep the code clean and formatted.

# support us

* yoomoney: https://yoomoney.ru/to/4100117354062028

# contacts

* telegram chat: https://t.me/TTMediaBot_chat
* E-mail: TTMediaBot@gmail.com
