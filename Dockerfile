FROM python:3.13.7-slim

COPY . /app
WORKDIR /app

RUN ["pip", "install", "-r", "requirements.txt"]

CMD ["python", "./main.py"]