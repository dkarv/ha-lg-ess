FROM homeassistant/home-assistant:2026.6

RUN apk add inotify-tools

COPY ./start.sh /start.sh

ENTRYPOINT ["/start.sh"]
