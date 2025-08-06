import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime


class ReminderDB:
    """Singleton to handle accessing and storing reminders"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ReminderDB, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        host="db",
        port=5432,
        user="sigpwny",
        password="sigpwny",
        dbname="db",
    ):
        self.conn = psycopg2.connect(
            host=host, port=port, user=user, password=password, dbname=dbname
        )
        self._ensure_table()
        self.reminders = self.load_reminders()

    def _ensure_table(self):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS reminders (
                    id SERIAL PRIMARY KEY,
                    remind_at TIMESTAMPTZ NOT NULL,
                    message TEXT NOT NULL,
                    channel_id BIGINT NOT NULL,
                    author_id BIGINT NOT NULL
                )
            """
            )
            self.conn.commit()

    def load_reminders(self):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, remind_at, message, channel_id, author_id FROM reminders"
            )
            rows = cur.fetchall()
        for r in rows:
            if isinstance(r["remind_at"], str):
                r["remind_at"] = datetime.fromisoformat(r["remind_at"])
        return rows

    def add_reminder(
        self, remind_at: datetime, message: str, channel_id: int, author_id: int
    ):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO reminders (remind_at, message, channel_id, author_id) VALUES (%s, %s, %s, %s) RETURNING id",
                (remind_at, message, channel_id, author_id),
            )
            reminder_id = cur.fetchone()[0]  # type: ignore
            self.conn.commit()
        self.reminders.append({"id": reminder_id, "remind_at": remind_at, "message": message, "channel_id": channel_id, "author_id": author_id})  # type: ignore
        return reminder_id

    def get_reminders_by_author_id(self, author_id: int):
        return [r for r in self.reminders if r["author_id"] == author_id]

    def remove_reminder(self, reminder_id: int):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM reminders WHERE id = %s", (reminder_id,))
            self.conn.commit()
        self.reminders = [r for r in self.reminders if r["id"] != reminder_id]

    def get_all_reminders(self):
        return self.reminders
    
    def get_reminder_by_id(self, reminder_id: int):
        for r in self.reminders:
            if r["id"] == reminder_id:
                return r
        return None
