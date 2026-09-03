set -euo pipefail

cd ~/pwnybot
git pull --ff-only
docker compose up --build -d pwnybot db
