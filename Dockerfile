FROM python:3.13.7-slim

ENV TZ=Asia/Krasnoyarsk

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN ["pip", "install", "-r", "requirements.txt"]

COPY . /app


CMD ["python", "./main.py"]