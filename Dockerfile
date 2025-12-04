FROM python:3.13.7-slim

ENV TZ=Asia/Krasnoyarsk
RUN ["apt", "update"]
RUN ["apt", "install", "-y", "gettext-base"]
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN ["pip", "install", "-r", "requirements.txt"]


COPY . /app

ENTRYPOINT ["sh", "./docker_entrypoint.sh"]