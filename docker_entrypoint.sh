#!/bin/bash
export $(cat .env | xargs)

TEMPLATE="./files/nginx.conf.example"
OUTPUT="./files/nginx.conf"

rm -f "$OUTPUT"

cp "$TEMPLATE" "$OUTPUT"


for var in $(compgen -e); do
    value=$(printenv "$var")

    safe_value=$(printf '%s\n' "$value" | sed 's/[[\.*^$/]/\\&/g')

    sed -i "s|\${$var}|$safe_value|g" "$OUTPUT"
done
