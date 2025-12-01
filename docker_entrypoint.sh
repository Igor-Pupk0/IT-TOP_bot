#!/bin/bash
export $(cat .env | xargs)
# Указываем файл для обработки
FILE="./files/nginx.conf.example"

# Или использовать envsubst, если он установлен
envsubst < "$FILE" > ./files/nginx.conf