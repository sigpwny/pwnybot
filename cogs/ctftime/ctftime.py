from datetime import datetime
import time
import requests

import discord
from discord.ext import commands
from discord.ext.commands import Bot

from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

# MongoDB handle
from lib.util import command_decorator, subcommand_decorator

USER_AGENT = 'pwnybot'


class CTFTime(commands.Cog):
    """This cog provides information about ongoing/upcoming events, as well as a
    specific year's leaderboard.
    """

    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        self.session = requests.Session()
        self.session.headers.update({'user-agent': USER_AGENT})

    @subcommand_decorator()
    async def current(self, ctx: SlashContext) -> None:
        """Show ongoing CTF competitions"""

        await ctx.defer()
        ONE_WEEK = 60 * 60 * 24 * 7
        url = f'https://ctftime.org/api/v1/events/?limit=10&start={round(time.time()) - ONE_WEEK}&finish={round(time.time()) + ONE_WEEK}'
        events = self.session.get(url).json()

        no_running_events = True
        for event in events:
            start_date = datetime.strptime(
                event['start'][:-6], '%Y-%m-%dT%H:%M:%S')
            end_date = datetime.strptime(
                event['end'][:-6], '%Y-%m-%dT%H:%M:%S')
            if start_date < datetime.now() and end_date > datetime.now():
                # Convert timestamps to dates
                start = start_date.strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
                end = end_date.strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
                embed = (
                    discord.Embed(
                        title=f"🔴 {event['title']} is live",
                        description=(
                            f"Event website: {event['url']}\n"
                            f"CTFtime URL: {event['ctftime_url']}"
                        ),
                        color=discord.Colour.red(),
                    )
                    .set_thumbnail(url=event["logo"])
                    .add_field(name="Description", value=event["description"], inline=False)
                    .add_field(
                        name="Format",
                        value=f"{event['location']} {event['format']}",
                        inline=True,
                    )
                    .add_field(
                        name="Organizers",
                        value=", ".join(
                            map(lambda organizer: organizer["name"], event["organizers"])),
                        inline=True,
                    )
                    .add_field(name="Weight", value=event["weight"], inline=True)
                    .add_field(
                        name="Timeframe",
                        value=f'{start} -> {end}',
                        inline=True,
                    )
                )
                no_running_events = False
                await ctx.send(embed=embed)
        if no_running_events:
            await ctx.send("No ongoing CTFs for the moment.")

    @subcommand_decorator(
        limit={
            'description': 'Number of events to fetch (default: 3, max: 15)'}
    )
    async def upcoming(self, ctx: SlashContext, limit: int = 3) -> None:
        """Show upcoming events
        """
        await ctx.defer()

        limit = min(limit, 15)
        no_upcoming_events = True

        url = f'https://ctftime.org/api/v1/events/?limit={limit}&start={round(time.time())}'
        events = self.session.get(url).json()

        for event in events:
            # Convert timestamps to dates
            start = datetime.strptime(
                event['start'][:-6], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
            end = datetime.strptime(event['finish'][:-6], '%Y-%m-%dT%H:%M:%S').strftime(
                '%Y-%m-%d %H:%M:%S') + ' UTC'
            embed = (
                discord.Embed(
                    title=f"🆕 {event['title']}",
                    description=(
                        f"Event website: {event['url']}\n"
                        f"CTFtime URL: {event['ctftime_url']}"
                    ),
                    color=discord.Colour.red(),
                )
                .set_thumbnail(url=event["logo"])
                .add_field(name="Description", value=event["description"], inline=False)
                .add_field(
                    name="Format",
                    value=f"{event['location']} {event['format']}",
                    inline=True,
                )
                .add_field(
                    name="Organizers",
                    value=", ".join(
                        map(lambda organizer: organizer["name"], event["organizers"])),
                    inline=True,
                )
                .add_field(name="Weight", value=event["weight"], inline=True)
                .add_field(
                    name="Timeframe",
                    value=f'{start} -> {end}',
                    inline=True,
                )
            )
            no_upcoming_events = False
            await ctx.send(embed=embed)

        if no_upcoming_events:
            await ctx.send("No upcoming CTFs.")

    @subcommand_decorator(
        year={'description': "Leaderboard's year"}
    )
    async def top(self, ctx: SlashContext, year: int = None) -> None:
        """Shows CTFtime's leaderboard for a specific year"""
        await ctx.defer()
        year = year or datetime.today().year
        year = str(year)

        url = f'https://ctftime.org/api/v1/top/{year}/'
        teams = self.session.get(url).json()[year]

        leaderboard = f"{'[Rank]':<10}{'[Team]':<50}{'[Score]'}\n"

        for rank, team in enumerate(teams, start=1):
            score = round(team["points"], 4)
            leaderboard += f"{rank:<10}{team['team_name']:<50}{score}\n"

        await ctx.send(
            f":triangular_flag_on_post:  **{year} CTFtime Leaderboard**"
            f"```ini\n{leaderboard.strip()}```"
        )


def setup(bot: Bot) -> None:
    """Add the extension to the bot."""
    bot.add_cog(CTFTime(bot))
