# PWNYBOT

SigPWNYs discord bot

### Setup

Create a `.env` file like this:


```
DISCORD_TOKEN=ODXXXXA4XXXXOXXXXM0XXAx.YXXXwA.V_CXXXXXXXXXXX
CTFD_TOKEN=dXXXX85dXXXX3c5XXXX4b80bXXXXf4b75fXXXXXXXXXXXXX
```

### Running Locally

```
docker-compose up --build -d pwnybot
```

Alternatively, set the environment variables on your machine then run:

```
pip install --no-cache-dir -r requirements.txt
python3 main.py
```
### Using on another SSH server

In github, set these environment variables:

+ `SSH_PRIVATE_KEY`
+ `SERVER_USER`
+ `SERVER_IP`
+ `SSH_KNOWN_HOSTS` - (run `ssh-keyscan host` on server)

### Using elsewhere

Set `GUILD_IDS` and `INTERNAL_CTFD_URL` in `lib/config.py`.
