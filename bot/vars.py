import os

app_name = "TTMediaBot"
app_version = '1.0.0'
client_name = app_name + "-V" + app_version
loop_timeout = 0.01
max_message_length = 256
history_max_lenth = 128

directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
