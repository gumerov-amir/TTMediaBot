import datetime
import sys
from click import echo
from bot.player import Player
from TeamTalkPy import TeamTalk


class Logger:
    def __init__(self, file_name):
        self.origenal = sys.stdout
        self.file_name = file_name

    def write(self, text):
        self.origenal.write(text)
        if text != "\n":
            text = text + "\n"
            with open(self.file_name, "a", encoding='utf-8') as f:
                f.write("{time}: {text}".format(time=datetime.datetime.now(), text=text))

def echo_dict(d, indent_level=0):
    for n, k in enumerate(list(d)):
        echo("{}{}: {}".format("   " * indent_level, n,k))

def echo_devices():
    player = Player(TeamTalk(), None)
    echo("Input devices:")
    echo_dict(player.input_devices, indent_level=1)
    echo()
    echo("Output devices:")
    echo_dict(player.output_devices, indent_level=1)


