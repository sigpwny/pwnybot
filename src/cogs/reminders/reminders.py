from interactions import Extension, Permissions, SlashContext, BaseUser, Embed
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

def get_reminder_channel(reminder):
    if reminder["silent"]:
        return "dm"
    
    return f"<#{reminder['channel_id']}>"

class Reminders(Extension):
    """Commands for creating reminders"""

    @subcommand(
        when={
            "description": "When the reminer should be triggered. Format: (1w2d3h4m5s)"
        },
        message={"description": "What message should be attached to the reminder?"},
        silent={"description": "Should the reminder be dmed?"}
    )
    async def create(self, ctx: SlashContext, when: str, message: str, silent: bool = False):
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
            silent=silent
        )

        await ctx.send("Reminder is queued!", ephemeral=True)

    @subcommand(
        user={
            "description": "User whose reminders you would like to view, default is all users."
        }
    )
    async def list(self, ctx: SlashContext, user: BaseUser | None = None):
        """List the scheduled reminders for all users or a particular user"""

        if not any(str(role.id) in MODERATOR_ROLES for role in ctx.author.roles):  # type: ignore
            await ctx.send(
                "You do not have permission to use this command.", ephemeral=True
            )
            return

        db = ReminderDB()

        if user is None:
            reminders = db.get_all_reminders()
        else:
            reminders = db.get_reminders_by_author_id(user.id)

        description = ""
        for reminder in reminders:
            description += f"{reminder['id']}: {get_reminder_channel(reminder)}: '{reminder['message']}' <t:{int(reminder['remind_at'].timestamp())}:R>\n"
        
        embed = Embed(
            title="Reminders" + f" for {user.display_name}" if user else "",
            description=description or "There are no reminders currently for this query"
        )
        
        await ctx.send(embed=embed, ephemeral=True)

    @subcommand(
        reminder_id={
            "description": "The ID of the reminder to delete"
        }
    )
    async def delete(self, ctx: SlashContext, reminder_id: int):
        """Delete a reminder by its ID"""
        
        if not any(str(role.id) in MODERATOR_ROLES for role in ctx.author.roles):  # type: ignore
            await ctx.send(
                "You do not have permission to use this command.", ephemeral=True
            )
            return

        db = ReminderDB()
        
        reminder_to_delete = db.get_reminder_by_id(reminder_id)
        
        if reminder_to_delete is None:
            await ctx.send(f"Reminder with ID {reminder_id} not found.", ephemeral=True)
            return
        
        if reminder_to_delete["author_id"] != ctx.author_id and not ctx.member.has_permission(Permissions.ADMINISTRATOR): # type: ignore
            await ctx.send("You can only delete your own reminders.", ephemeral=True)
            return
        
        db.remove_reminder(reminder_id)
        await ctx.send(f"Reminder {reminder_id} has been deleted successfully!", ephemeral=True)