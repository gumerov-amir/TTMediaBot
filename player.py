import vlc
import time

class Player:
    def __init__(self, ttclient, config):
        self.config = config
        self._ttclient = ttclient
        self._vlc_instance = vlc.Instance()
        self._vlc_player = self._vlc_instance.media_player_new()
        self._vlc_player.audio_set_volume(int(self.config["default_volume"]))
        self.max_volume = int(self.config["max_volume"])
        self.faded_volume = bool(self.config["faded_volume"])
        self.faded_volume_timestamp = float(self.config["faded_volume_timestamp"])
        self.seek_step = float(config["seek_step"])
        self.output_devices = self.get_output_devices()
        self.input_devices = self.get_input_devices()
        self.output_device = int(self.config["output_device"])
        self.input_device = int(self.config["input_device"])
        self.track_data = {}
        self.state = "Stopped"

    def play(self, url=None, artist=None, title=None):
        self.state = "Playing"
        self.initialize_devices()
        if url== None:
            self._play_in_teamtalk(self.track_data["artist"], self.track_data["title"])
            self._vlc_player.play()
        else:
            self._play_in_teamtalk(artist, title)
            self._play_with_vlc(url)
            self.track_data = {"artist": artist, "title": title}
        time.sleep(1)
        while self._vlc_player.get_state() == vlc.State.Playing:
            time.sleep(1)
        if self._vlc_player.get_state() == vlc.State.Ended:
            self._stop_in_teamtalk()
            self.state = "Stopped"




    def pause(self):
        self.state = "Paused"
        self._vlc_player.pause()
        self._pause_in_teamtalk()

    def stop(self):
        self.state = "Stopped"
        self.track_data = {}
        self._stop_in_teamtalk()
        self._vlc_player.pause()

    def _play_in_teamtalk(self, artist, title):
        self._ttclient.enableVoiceTransmission(True)
        self._ttclient.doChangeStatus(0, "playing {} - {}".format(artist, title))

    def _pause_in_teamtalk(self):
        self._ttclient.enableVoiceTransmission(False)
        time.sleep(1)
        self._ttclient.doChangeStatus(0, "paused {} - {}".format(self.track_data["artist"], self.track_data["title"]))

    def _stop_in_teamtalk(self):
        self._ttclient.enableVoiceTransmission(False)
        self._ttclient.doChangeStatus(0, "")

    def _play_with_vlc(self, arg):
        self._vlc_player.set_media(self._vlc_instance.media_new(arg))
        self._vlc_player.play()

    def set_volume(self, volume):
        volume = volume if volume <= self.max_volume else self.max_volume
        if self.faded_volume:
            n = 1 if self._vlc_player.audio_get_volume() < volume else -1
            for i in range(self._vlc_player.audio_get_volume(), volume, n):
                self._vlc_player.audio_set_volume(i)
                time.sleep(self.faded_volume_timestamp)
        else:
            self._vlc_player.audio_set_volume(volume)

    def seek_back(self, time_step=0):
        time_step = time_step if time_step  != 0 else self.seek_step
        pos = self._vlc_player.get_position() - time_step
        if pos < 0:
            pos = 0
        elif pos > 1:
            pos = 1
        self._vlc_player.set_position(pos)

    def seek_forward(self, time_step=0):
        time_step = time_step if time_step  != 0 else self.seek_step
        pos = self._vlc_player.get_position() + time_step
        if pos < 0:
            pos = 0
        elif pos > 1:
            pos = 1
        self._vlc_player.set_position(pos)

    def get_output_devices(self):
        devices = {}
        mods = self._vlc_player.audio_output_device_enum()
        if mods:
            mod = mods
            while mod:
                mod = mod.contents
                devices[str(mod.description, "utf-8")] = mod.device
                mod = mod.next
        vlc.libvlc_audio_output_device_list_release(mods)
        return devices

    def get_input_devices(self):
        devices = {}
        device_list = [i for i in self._ttclient.getSoundDevices()]
        for device in device_list:
            devices[device.szDeviceName] = device.nDeviceID
        return devices

    def initialize_devices(self):
        self._vlc_player.audio_output_device_set(None, self.output_devices[list(self.output_devices)[self.output_device]])
        self._ttclient.initSoundInputDevice(self.input_devices[list(self.input_devices)[self.input_device]])
