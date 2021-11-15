# PWNYBOT

The official sigPWNY discord bot.
### Installation

+ Clone from github
+ Create a `.env` file like this:

Note that the bot is still partially functional without `CTFD_TOKEN` or `DEFAULT_ARCHIVE_ID` being defined.

```
DISCORD_TOKEN=XXXXXX
CTFD_TOKEN=XXXXXX
DEFAULT_ARCHIVE_ID=XXXXXX
GUILD_IDS=GUILD1,GUILD2
```


### Usage

##### With docker

```
docker-compose up -d pwnybot
```

##### Local testing


```
git clone git@github.com:sigpwny/pwnybot.git
cd pwnybot
pip install --no-cache-dir -r requirements.txt
DISCORD_TOKEN=XXXXXX CTFD_TOKEN=XXXXXXDEFAULT_ARCHIVE_ID=XXXXXX GUILDIDS=GUILD1,GUILD2 python3 main.py
```

##### Interested in helping?

+ Check the issues for feature requests and bugs
+ Create a branch and submit a PR.
+ Please do not push directly to master! (This will redeploy pwnybot with potentially broken code :0)
+ Check out the `cogs/template` directory for a starting point.

### Features

+ "portal" system
+ CTFtime scraper
+ Encoding / Binary / Cipher / XKCD / Syscall table utility methods
+ Breakout Rooms
+ Complete CTF competition management system