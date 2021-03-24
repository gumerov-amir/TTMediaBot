import click

from bot import Bot


@click.command()
@click.option("-c", help="config file", default="config.json")
@click.option("--devices", is_flag=True)
def cli(c="config.ini", devices=False):
    bot = Bot(c)
    if devices:
        echo_sound_devices(bot.sound_device_manager)
    else:
        bot.initialize()
        bot.run()


def echo_sound_devices(sound_device_manager):
    print('Output devices:')
    for i, device in enumerate(sound_device_manager.output_devices):
        print('\t{index}: {name}'.format(index=i, name=device.name))
    print()
    print('Input devices:')
    for i, device in enumerate(sound_device_manager.input_devices):
        print('\t{index}: {name}'.format(index=i, name=device.name))


if __name__ == "__main__":
    cli()
