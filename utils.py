from click import echo
from player import Player
from TeamTalkPy import TeamTalk


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


