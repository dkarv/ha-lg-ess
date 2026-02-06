FROM homeassistant/home-assistant:2026.2

RUN apk add inotify-tools

COPY ./start.sh /start.sh
COPY ./bootstrap.sh /bootstrap.sh

ENTRYPOINT ["/start.sh"]
