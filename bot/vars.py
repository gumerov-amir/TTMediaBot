import enum
import os

version = '1.0.0'
loop_timeout = 0.01
max_message_length = 256
history_max_lenth = 128

directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

default_cache_file_name = os.path.join(directory, "TTMediaBotCache.dat")

