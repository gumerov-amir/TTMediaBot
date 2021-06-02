FROM debian:buster-slim
RUN apt-get update && apt-get upgrade -y && apt-get install -y pulseaudio vlc-bin vlc-plugin-base p7zip python3 python3-pip python3-setuptools --no-install-recommends && apt autoclean && apt clean && rm -rf /var/lib/apt/lists
RUN useradd -ms /bin/bash ttbot
USER ttbot
WORKDIR /home/ttbot
COPY . .
RUN pip3 install -r requirements.txt
RUN python3 tools/ttsdk_downloader.py
CMD pulseaudio -D && ./TTMediaBot.sh
