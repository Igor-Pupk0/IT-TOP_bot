#!/bin/sh

TEMPLATE="./files/nginx.conf.example"
OUTPUT="./files/default.conf"

mkdir -p /etc/nginx/conf.d

export $(cat .env | xargs)

cp "$TEMPLATE" "$OUTPUT"

safe_replace() {
    local var_name="$1"
    local value="$2"
    value_escaped=$(printf '%s' "$value" | sed 's/[&/\]/\\&/g')
    sed -i "s@\${$var_name}@${value_escaped}@g" "$OUTPUT"
}

# Выполняем замены
safe_replace "WEBHOOK_DOMAIN" "$WEBHOOK_DOMAIN"
safe_replace "WEBHOOK_ENDPOINT" "$WEBHOOK_ENDPOINT"

python ./main.py