import vlc
import time

class Player:
    def __init__(self, ttclient, output_device, input_device):
        self.output_device = output_device
        self.input_device = input_device
        self._ttclient = ttclient
        self._vlc_instance = vlc.Instance()
        self._vlc_player = self._vlc_instance.media_player_new()
        self._vlc_player.audio_set_volume(50)
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
        self._vlc_player.stop()

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
        output_devices = self.get_output_devices()
        self._vlc_player.audio_output_device_set(None, output_devices[list(output_devices)[self.output_device]])
        input_devices = self.get_input_devices()
        self._ttclient.initSoundInputDevice(input_devices[list(input_devices)[self.input_device]])
