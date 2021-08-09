# PWNYBOT

SigPWNYs discord bot

### Using elsewhere

+ Generate your own DISCORD_TOKEN and add the bot to your server.
+ Then follow one of the guides below

### Set for docker

Create a `.env` file like this:


```
DISCORD_TOKEN=ODXXXXA4XXXXOXXXXM0XXAx.YXXXwA.V_CXXXXXXXXXXX
CTFD_TOKEN=dXXXX85dXXXX3c5XXXX4b80bXXXXf4b75fXXXXXXXXXXXXX
DEFAULT_ARCHIVE_ID=123413213123
GUILD_IDS=GUILD1,GUILD2
```

```
docker-compose up --build -d pwnybot
```

### Local testing


```
git clone git@github.com:sigpwny/pwnybot.git
cd pwnybot
pip install --no-cache-dir -r requirements.txt
DISCORD_TOKEN=ODXXXXA4XXXXOXXXXM0XXAx.YXXXwA.V_CXXXXXXXXXXX CTFD_TOKEN=dXXXX85dXXXX3c5XXXX4b80bXXXXf4b75fXXXXXXXXXXXXX DEFAULT_ARCHIVE_ID=123413213123 GUILDIDS=GUILD1,GUILD2 python3 main.py
```

### Modifying pwnybot on sigpwny

+ For small fixes, push them directly to master.
+ Otherwise, please contact @reteps so he can disable the docker while you run it locally and test. This prevents duplicating commands / other weirdness.
+ 