from argparse import ArgumentParser
from pathlib import Path

from bot import Bot, app_vars
from bot.config import save_default_file
from bot.sound_devices import SoundDeviceManager

parser = ArgumentParser()
parser.add_argument(
    "-c",
    "--config",
    help="Path to the configuration file",
    default=Path(app_vars.directory) / "config.json",
)
parser.add_argument("-C", "--cache", help="Path to the cache file", default=None)
parser.add_argument("-l", "--log", help="Path to the log file", default=None)
parser.add_argument(
    "--devices",
    help="Show available devices and exit",
    action="store_true",
)
parser.add_argument(
    "--default-config",
    help='Save default config to "config_default.json" and exit',
    action="store_true",
)
args = parser.parse_args()


def main(
    config: str = args.config,
    cache: str | None = args.cache,
    log: str | None = args.log,
    devices: bool = args.devices,
    default_config: bool = args.default_config,
) -> None:
    if devices:
        bot = Bot(None, None, None)
        echo_sound_devices(bot.sound_device_manager)
    elif default_config:
        save_default_file()
    else:
        bot = Bot(config, cache, log)
        bot.initialize()
        try:
            bot.run()
        except KeyboardInterrupt:
            bot.close()


def echo_sound_devices(sound_device_manager: SoundDeviceManager) -> None:
    for _i, _device in enumerate(sound_device_manager.output_devices):
        pass
    for _i, _device in enumerate(sound_device_manager.input_devices):
        pass


if __name__ == "__main__":
    main()
