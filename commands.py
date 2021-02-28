import re
from threading import Thread



class ProcessCommand:
    help = """help text of ttmediabot"""

    def __init__(self, player, vk_audio):
        self.player = player
        self.vk_audio = vk_audio


    def __call__(self, message):
        commands_dict = {"p": self.play_pause, "s": self.stop, "r": self.rate, "u": self.play_by_url, "v": self.volume, "b": self.back, "f": self.forward, "h": lambda arg: ProcessCommand.help}
        try:
            command = re.findall("[a-z]+", message.split(" ")[0].lower())[0]
        except IndexError:
            return ProcessCommand.help
        arg = " ".join(message.split(" ")[1::])
        try:
            return commands_dict[command](arg)
        except KeyError:
            return "Unknown command.\n" + ProcessCommand.help
        except Exception as e:
            print("error in process_command: ", e)
            return "error: {}".format(e)

    def play_pause(self, arg):
        if arg:
            return self.play_from_vk(arg)
        else:
            if self.player.state == "Playing":
                return self.player.pause()
            elif self.player.state == "Paused":
                playing_thread = Thread(target=self.player.play)
                playing_thread.start()
                return

    def play_from_vk(self, arg):
        # vk_track_list = []
        vk_track_list_iter = self.vk_audio.search_iter(arg)
        try:
            track = next(vk_track_list_iter)
            playing_thread = Thread(target=self.player.play, args=(track["url"], track["artist"], track["title"]))
            playing_thread.start()
            #vk_track_list.append(track)
            return
        except StopIteration:
            return "По вашему запросу ничего не найдено"
        except TypeError:
            return "error: {}".format(track)

    def rate(self, arg):
        try:
            self.player._vlc_player.set_rate(float(arg))
        except ValueError:
            return "Введите число, используйте ."

    def play_by_url(self, arg):
        playing_thread = Thread(target=self.player.play, args=(arg, "", arg))
        playing_thread.start()

    def stop(self, arg):
        self.player.stop()

    def volume(self, arg):
        try:
            self.player.set_volume(int(arg))
        except ValueError:
            return "Укажите число"

    def forward(self, arg):
        try:
            if arg:
                self.player.seek_forward(abs(int(arg)) / 100)
            else:
                self.player.seek_forward()
        except ValueError:
            return "Введите число от 1 до 100"

    def back(self, arg):
        try:
            if arg:
                self.player.seek_back(abs(int(arg)) / 100)
            else:
                self.player.seek_back()
        except ValueError:
            return "Введите число от 1 до 100"



    def next(self, arg):
        pass


