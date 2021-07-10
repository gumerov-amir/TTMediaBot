import click

from bot import Bot
from bot.config import save_default_file


@click.command()
@click.option("-c", "--config", help='Path to the configuration file', default='config.json')
@click.option("--cache", help='Path to the cache file', default=None)
@click.option("--log", help='Path to the log file', default=None)
@click.option("--devices", help='Show available devices and exit', is_flag=True)
@click.option("--default-config", help="Save default config to \"config_default.json\" and exit", is_flag=True)
def main(config, cache, log, devices, default_config):
    if devices:
        bot = Bot(None, None, None)
        echo_sound_devices(bot.sound_device_manager)
    elif default_config:
        save_default_file()
        print("Successfully dumped to config_default.json")
    else:
        bot = Bot(config, cache, log)
        bot.initialize()
        try:
            bot.run()
        except KeyboardInterrupt:
            bot.close()


def echo_sound_devices(sound_device_manager):
    print('Output devices:')
    for i, device in enumerate(sound_device_manager.output_devices):
        print('\t{index}: {name}'.format(index=i, name=device.name))
    print()
    print('Input devices:')
    for i, device in enumerate(sound_device_manager.input_devices):
        print('\t{index}: {name}'.format(index=i, name=device.name))


if __name__ == "__main__":
    main()
