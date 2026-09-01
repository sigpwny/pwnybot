#!/bin/sh
set -eu

if [ "${V2_CUTOVER_APPROVED:-}" != "true" ]; then
  echo "Refusing v2 cutover. Drain or migrate PostgreSQL reminders, then set V2_CUTOVER_APPROVED=true."
  exit 1
fi

cd "$HOME/pwnybot"
git pull
docker compose build pwnybot
docker compose run --rm pwnybot node dist/scripts/register-discord-commands.js
docker compose up -d pwnybot
