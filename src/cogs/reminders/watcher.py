import asyncio
from datetime import datetime, timezone
from cogs.reminders.db import ReminderDB
from interactions import Client


async def callback(bot: Client, reminder):
    channel = await bot.fetch_channel(reminder["channel_id"])
    await channel.send(reminder["message"])  # type: ignore


async def reminder_watcher(bot: Client, interval=1):
    reminder_db = ReminderDB()
    while True:
        now = datetime.now(timezone.utc)
        due = [r for r in reminder_db.get_all_reminders() if r["remind_at"] <= now]
        for reminder in due:
            await callback(bot, reminder)
            reminder_db.remove_reminder(reminder["id"])
        await asyncio.sleep(interval)
