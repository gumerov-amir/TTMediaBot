import os

app_name = "TTMediaBot"
app_version = '1.0.0'
client_name = app_name + "-V" + app_version
about_text = lambda: _("""\
TTMediaBot - bot for music streaming in TeamTalk.
Authors: Gumerov_amir, A11CF0.\
""")
loop_timeout = 0.01
max_message_length = 256
history_max_lenth = 128

directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
