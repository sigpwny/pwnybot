cd ~/pwnybot
git pull
docker system prune -f
docker-compose up --build --no-deps --force-recreate -d pwnybot
