FROM debian:bullseye-slim
RUN apt update \
&& apt upgrade -y \
&& apt install -y --no-install-recommends \
gettext \
libmpv1 \
p7zip \
pulseaudio \
python3 \
python3-pip \
python3-setuptools \
 && apt autoclean \
&& apt clean \
&& rm -rf /var/lib/apt/list
RUN useradd -ms /bin/bash ttbot
USER ttbot
WORKDIR /home/ttbot
COPY --chown=ttbot requirements.txt .
RUN pip3 install -r requirements.txt
COPY --chown=ttbot . .
RUN python3 tools/ttsdk_downloader.py && python3 tools/compile_locales.py
CMD pulseaudio -D && ./TTMediaBot.sh -c data/config.json --cache data/TTMediaBotCache.dat --log data/TTMediaBot.log
