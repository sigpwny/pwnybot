from interactions import Extension, SlashContext, BaseUser, Embed
from cogs.reminders.db import ReminderDB
from lib.util import subcommand
from lib.config import MODERATOR_ROLES
import re
from datetime import datetime, timedelta, timezone


def parse_duration(duration_str):
    pattern = r"(?:(\d+)w)?(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?"
    match = re.fullmatch(pattern, duration_str)
    if not match:
        return None
    weeks, days, hours, minutes, seconds = (int(x) if x else 0 for x in match.groups())
    return timedelta(
        weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds
    )


class Reminders(Extension):
    """Commands for creating reminders"""

    @subcommand(
        when={
            "description": "When the reminer should be triggered. Format: (1w2d3h4m5s)"
        },
        message={"description": "What message should be attached to the reminder?"},
    )
    async def create(self, ctx: SlashContext, when: str, message: str):
        """Create a reminder"""

        if not any(str(role.id) in MODERATOR_ROLES for role in ctx.author.roles):  # type: ignore
            await ctx.send(
                "You do not have permission to use this command.", ephemeral=True
            )
            return

        delta = parse_duration(when)
        if delta is None or delta.total_seconds() <= 0:
            await ctx.send(
                "Invalid time format. Please use something like '1w2d3h4m5s'.",
                ephemeral=True,
            )
            return

        reminder_time = datetime.now(timezone.utc) + delta

        db = ReminderDB()
        db.add_reminder(
            remind_at=reminder_time,
            message=f"Reminder for <@{ctx.author_id}>: {message}",
            channel_id=ctx.channel_id,
            author_id=ctx.author_id,
        )

        await ctx.send("Reminder is queued!", ephemeral=True)

    @subcommand(
        user={
            "description": "User whose reminders you would like to view, default is all users."
        }
    )
    async def list(self, ctx: SlashContext, user: BaseUser | None = None):
        """List the scheduled reminders for all users or a particular user"""
        db = ReminderDB()

        if user is None:
            reminders = db.get_all_reminders()
        else:
            reminders = db.get_reminders_by_author_id(user.id)

        description = ""
        for reminder in reminders:
            description += f"{reminder['id']}: <#{reminder['channel_id']}>: '{reminder['message']}' <t:{int(reminder['remind_at'].timestamp())}:R>\n"
        
        embed = Embed(
            title="Reminders" + f" for {user.display_name}" if user else "",
            description=description or "There are no reminders currently for this query"
        )
        
        await ctx.send(embed=embed)