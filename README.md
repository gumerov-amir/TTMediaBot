# TTMediaBot - Fork by Nuno Costa

A media streaming bot for TeamTalk 5, forked from the original TTMediaBot by Amir Gumerov.

**Repository:** https://www.github.com/nunotfc/TTMediaBot

## What's different from the original

This fork focuses on **stability**, **performance**, and **YouTube Music support**:

- **Queue mode** (`m q`): play tracks in order, enqueue with `q +`, remove with `q -N`, clear with `q c`
- **Update command** (`/update` or `/upd`): checks pip updates and restarts the bot if packages changed
- **Bass boost** (`/bb 0-10`): adjustable bass boost with persistence in config
- **Pitch control** (`/pi -12 to +12`): semitone pitch shifting during playback
- **Position saving** (`/ep`): resume tracks from where you paused/stopped
- **Command chaining**: use `|` to run multiple commands (e.g., `t | v 30`)
- **Split cache**: separate files for recents, favorites, queue and metadata — no more single giant .dat
- **Performance fixes**: memory leak fix in track references, CPU usage reduced by 90%, queue and track list capped at 1000 items
- **Race condition fix**: bot now waits for channel join before processing startup commands
- **Resilient cache**: corrupted pickle files no longer crash the bot
- **Dropbox support**: stream audio directly from Dropbox URLs

Original authors: Amir Gumerov, Vladislav Kopylov, Beqa Gozalishvili, Kirill Belousov.

---

## Installation and usage
### Requirements
* Python 3.7 or later;
* TeamTalk SDK (downloaded automatically by ttsdk_downloader.py). On Linux, install p7zip or p7zip-full first; on Windows, install 7-Zip;
* On Linux: pulseaudio and libmpv (`libmpv1` on Debian-based systems);
* On Windows: a virtual audio cable driver (e.g., VB-Cable) and the mpv library (installable via libmpv_win_downloader.py).

### Installation
* Clone this repository;
* Install Python requirements: `pip install -r requirements.txt`;
* Run `python tools/ttsdk_downloader.py`;
* On Windows, also run `python tools/libmpv_win_downloader.py`;
* Copy or rename `config_default.json` to `config.json`;
* Fill in all required fields in `config.json`;
* On Linux: `./TTMediaBot.sh --devices` to list audio devices;
* On Windows: `python TTMediaBot.py --devices`;
* Edit `config.json` with the correct device numbers.

### Usage
* On Linux: `./TTMediaBot.sh`
* On Windows: `python TTMediaBot.py`

### Running in Docker
Build the image:
```sh
docker build -t ttmediabot .
```
Then run:
```sh
docker run --rm --name ttmb_1 -v <path/to/data>:/home/ttbot/data ttmediabot
```
`<path/to/data>` should contain your `config.json`. Cache and log files will also be stored there.

## Startup options
* `--devices` - List all available input/output audio devices;
* `-c PATH` - Set a custom path to the configuration file.

## Config file options
* `language` - Bot interface language (requires matching locale folder);
* `sound devices` - Audio device numbers (connect output to input via virtual cable or pulseaudio);
* `player` - Player settings: default volume, max volume, bass boost, etc;
* `teamtalk` - TeamTalk server connection and login settings;
* `services` - Configure available music search/playback services;
* `logger` - Logging configuration.

## Pulse audio or VB cable settings
### Linux
* Install pulseaudio, then:
```sh
pulseaudio --start
pacmd load-module module-null-sink
```
* Run `./TTMediaBot.sh --devices` — output should be "null audio output", input should be "pulse".

### Windows
* Install VB-Cable, run `python TTMediaBot.py --devices`, and use the correct device numbers.
* Note: input device numbers may be duplicated — always pick the highest-numbered one for your output device.