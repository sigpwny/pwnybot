# PWNYBOT

The official sigpwny discord bot.
### Installation

1. Clone from github
2. If you haven't already, create a discord bot and then go to OAUTH 2 > URL Generator.

Check the 'bot' permission, and under bot you will need:

+ Manage Roles
+ Manage Channels
+ Read Messages/View Channels
+ Send Messages
+ Read Message History
+ Add Reactions

Additionally, go to the 'Bot' tab and enable the 'Message Content Intent'.

In the future, more permission may be needed, so ask the current maintainer.

Then, copy the link and invite the bot to your server.

2. Create a `.env` file like this:

```
DISCORD_TOKEN=XXXXXX
CTFD_TOKEN=XXXXXX
GUILD_IDS=GUILD1
```

Fill in the DISCORD_TOKEN with the token from the 'Bot' tab of the discord developer portal. Then, fill in the GUILD_IDS with a comma seperated list of each guild IDs you want the server running on. If you just have one, do `GUILD_IDS=xxxxxx`.

Note that the bot is still partially functional without `CTFD_TOKEN` being defined.

Using a role with perms higher than the level you need, make sure that `lib/config.py` has an accurate admin role ID. Some commands may not work if this is set incorrectly.


3. Startup docker with this command

```
docker-compose up -d pwnybot
```

Note that `docker-compose up -d --build pwnybot` can be helpful to force rebuild all dependencies.


##### Interested in helping?

+ Check the issues for feature requests and bugs
+ Create a branch and submit a PR.
+ Please do not push directly to master! (This will redeploy pwnybot with potentially broken code :0)
+ Check out the `cogs/template` directory for a starting point.
