#!/bin/bash
export $(cat .env | xargs)

TEMPLATE="./files/nginx.conf.example"
OUTPUT="./files/nginx.conf"

export WEBHOOK_DOMAIN="${WEBHOOK_DOMAIN:-example.com}"
export WEBHOOK_ENDPOINT="${WEBHOOK_ENDPOINT:-webhook}"

rm -f "$OUTPUT"

cp "$TEMPLATE" "$OUTPUT"


for var in $(compgen -e); do
    value=$(printenv "$var")

    safe_value=$(printf '%s\n' "$value" | sed 's/[[\.*^$/]/\\&/g')

    sed -i "s|\${$var}|$safe_value|g" "$OUTPUT"
done
