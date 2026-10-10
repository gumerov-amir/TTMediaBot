FROM python:3.11-slim-bookworm
RUN apt update \
    && apt upgrade -y \
    && apt install -y --no-install-recommends \
    gettext \
    libmpv2 \
    p7zip \
    pulseaudio \
    curl \
    unzip \
    && apt autoclean \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://deno.land/x/install/install.sh | sh \
    && cp $HOME/.deno/bin/deno /usr/local/bin/deno
RUN useradd -ms /bin/bash ttbot
USER ttbot
WORKDIR /home/ttbot
COPY --chown=ttbot requirements.txt .
RUN pip install -r requirements.txt
COPY --chown=ttbot . .
RUN python tools/ttsdk_downloader.py && python tools/compile_locales.py
RUN chmod +x /home/ttbot/TTMediaBot.sh /home/ttbot/docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["-c", "data/config.json", "--cache", "data/TTMediaBotCache.dat", "--log", "data/TTMediaBot.log"]