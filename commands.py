import re
import traceback
from threading import Thread



class ProcessCommand(object):
    def __init__(self, player, vk_audio):
        self.player = player
        self.vk_audio = vk_audio
        self.commands_dict = {"p": self.play_pause, "s": self.stop, "sb": self.seek_back, "sf": self.seek_forward, "r": self.rate, "v": self.volume, "u": self.play_by_url, "h": self.help}


    def __call__(self, message):
        try:
            command = re.findall("[a-z]+", message.split(" ")[0].lower())[0]
        except IndexError:
            return self.help()
        arg = " ".join(message.split(" ")[1::])
        try:
            return self.commands_dict[command](arg)
        except KeyError:
            return "Unknown command.\n" + self.help(
            )
        except Exception as e:
            traceback.print_exc()
            return f"error: {e}"

    def play_pause(self, arg):
        """Текст справки play pause"""
        if arg:
            self.play_from_vk(arg)
        else:
            if self.player.state == "Playing":
                self.player.pause()
            elif self.player.state == "Paused":
                playing_thread = Thread(target=self.player.play)
                playing_thread.start()

    def play_from_vk(self, arg):
        vk_results = self.vk_audio.audio.search(q=arg)
        vk_track_count = vk_results["count"]
        vk_track_list = vk_results["items"]
        try:
            if vk_track_count > 0:
                track = vk_track_list[0]
                playing_thread = Thread(target=self.player.play, args=(track["url"], track["artist"], track["title"]))
                playing_thread.start()
                #vk_track_list.append(track)
                return
            else:
                return "По вашему запросу ничего не найдено."
        except KeyError:
            return "Трэк не доступен"

    def rate(self, arg):
        """Изменяет скорость"""
        try:
            self.player._vlc_player.set_rate(float(arg))
        except ValueError:
            return "Введите число, используйте ."

    def play_by_url(self, arg):
        """Воиспроизводит поток по ссылке."""
        if len(arg.split("://")) == 2 and arg.split("://")[0] != "file":
            playing_thread = Thread(target=self.player.play, args=(arg,))
            playing_thread.start()
        elif not arg:
            return self.help()
        else:
            return "Введите коректный url или разрешённый протокол"

    def stop(self, arg):
        """Останавливает аудио"""
        self.player.stop()

    def volume(self, arg):
        """Изменяет Громкость"""
        try:
            self.player.set_volume(int(arg))
        except ValueError:
            return("Недопустимое значение. Укажите число от 1 до 100.")

    def seek_back(self, arg):
        try:
            self.player.seek_back(arg)
        except ValueError:
            return("Недопустимое значение. Укажите число от 1 до 100.")

    def seek_forward(self, arg):
        try:
            self.player.seek_forward(arg)
        except ValueError:
            return("Недопустимое значение. Укажите число от 1 до 100.")

    def next(self, arg):
        pass

    def help(self, arg=None):
        """Возращает справку"""
        help_strings = []
        for i in list(self.commands_dict):
            help_strings.append(
                "{}: {}".format(i, self.commands_dict[i].__doc__)
            )
        return "\n".join(help_strings)
