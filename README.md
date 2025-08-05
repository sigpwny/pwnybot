# PWNYBOT

The official sigpwny discord bot.
### Installation

1. Clone from github
2. If you haven't already, create a discord bot and then go to OAUTH 2 > URL Generator.

Check the 'bot' scope, and after doing so, the list of bot-specific permissions should pop up. You will need:

+ Manage Channels
+ Manage Roles
+ Manage Threads

Additionally, go to the 'Bot' tab and enable the 'Message Content Intent'.

In the future, more permission may be needed, so ask the current maintainer.

Then, copy the link and invite the bot to your server.

2. Create a `.env` file like this:

```
DISCORD_TOKEN=XXXXXX
GUILD_IDS=GUILD1_ID
CTF_CATEGORY_CHANNELS=CHANNEL1_ID
CTF_ROLES=ROLE1_ID
UIUC_ROLES=ROLE2_ID
MODERATOR_ROLES=ROLE3_ID
```

Fill in the `DISCORD_TOKEN` with the token from the 'Bot' tab of the discord developer portal. Then, fill in the `GUILD_IDS` with a comma seperated list of each guild IDs you want the server running on. If you just have one, do `GUILD_IDS=XXXXXX`. Same goes for `CTF_CATEGORY` (category channels), `CTF_ROLES` (roles that can access CTF channels), and `UIUC_ROLES` (roles that can gain CTF roles).


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
