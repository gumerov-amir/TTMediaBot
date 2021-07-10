import os

app_name = "TTMediaBot"
app_version = '2.0.0'
client_name = app_name + "-V" + app_version
about_text = lambda: _("""\
TTMediaBot - a media streaming bot for TeamTalk.
Authors: Gumerov_amir, A11CF0, Beqa Gozalishvili.
Home page: https://github.com/gumerov-amir/TTMediaBot\
""")
loop_timeout = 0.01
max_message_length = 256
recents_max_lenth = 32
tt_event_timeout = 2

directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
