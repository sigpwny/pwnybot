CREATE TABLE IF NOT EXISTS reminders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  remind_at INTEGER NOT NULL,
  available_at INTEGER NOT NULL,
  message TEXT NOT NULL,
  channel_id TEXT NOT NULL,
  author_id TEXT NOT NULL,
  silent INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing')),
  lease_until INTEGER,
  lease_token TEXT,
  attempts INTEGER NOT NULL DEFAULT 0,
  last_error TEXT
);

CREATE INDEX IF NOT EXISTS reminders_due_idx
  ON reminders (status, available_at);

CREATE INDEX IF NOT EXISTS reminders_author_idx
  ON reminders (author_id);
