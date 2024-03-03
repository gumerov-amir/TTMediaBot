FROM ubuntu:22.04

RUN apt update
RUN apt upgrade -y
RUN apt install -y gettext libmpv1 p7zip pulseaudio python3-pip
RUN apt autoclean
RUN rm -rf /var/lib/apt/list

# Create a user named 'ttbot' and set the working directory
RUN useradd -ms /bin/bash ttbot
USER ttbot
WORKDIR /home/ttbot

# Copy the requirements file and install dependencies
COPY --chown=ttbot requirements.txt .
RUN pip3 install -r requirements.txt

# Copy the rest of the application files
COPY --chown=ttbot . .

# Run necessary scripts
RUN python3 tools/ttsdk_downloader.py
RUN python3 tools/compile_locales.py

# Set the command to start the application
CMD pulseaudio --start && ./TTMediaBot.sh -c data/config.json --cache data/TTMediaBotCache.dat --log data/TTMediaBot.log
