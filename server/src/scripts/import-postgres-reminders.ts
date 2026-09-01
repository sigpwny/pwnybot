import { parseArgs } from "node:util";
import dotenv from "dotenv";
import Database from "better-sqlite3";
import { Client } from "pg";
import { SqliteStorage } from "../storage/sqlite.js";

dotenv.config({ path: "../.env" });
dotenv.config({ path: ".env", override: false });

interface SourceReminder {
  id: number;
  remindAt: number;
  message: string;
  channelId: string;
  authorId: string;
  silent: boolean;
}

const { values } = parseArgs({
  options: {
    target: { type: "string" },
    "sqlite-path": { type: "string", default: "data/local.sqlite" },
  },
});

if (!values.target || !["sqlite", "d1"].includes(values.target)) {
  throw new Error(
    "Usage: npm run db:import:postgres -- --target sqlite|d1 [--sqlite-path path]",
  );
}

const postgresUrl = process.env.POSTGRES_URL;
if (!postgresUrl) {
  throw new Error("Missing POSTGRES_URL");
}

const client = new Client({ connectionString: postgresUrl });
await client.connect();
let reminders: SourceReminder[];
try {
  const result = await client.query<{
    id: number;
    remind_at: Date | string;
    message: string;
    channel_id: string;
    author_id: string;
    silent: boolean | null;
  }>(
    "SELECT id, remind_at, message, channel_id, author_id, silent FROM reminders ORDER BY id",
  );
  reminders = result.rows.map((row) => {
    const remindAt = new Date(row.remind_at).getTime();
    if (!Number.isSafeInteger(remindAt)) {
      throw new Error(`Reminder ${row.id} has an invalid remind_at value`);
    }
    return {
      id: Number(row.id),
      remindAt,
      message: row.message,
      channelId: String(row.channel_id),
      authorId: String(row.author_id),
      silent: Boolean(row.silent),
    };
  });
} finally {
  await client.end();
}

if (values.target === "sqlite") {
  importSqlite(reminders, values["sqlite-path"]!);
} else {
  await importD1(reminders);
}

console.log(
  `Verified ${reminders.length} imported reminders. Source rows were not modified.`,
);

function importSqlite(reminders: SourceReminder[], path: string): void {
  const storage = new SqliteStorage(path);
  storage.migrate(process.env.MIGRATIONS_PATH ?? "migrations");
  const db = new Database(path);
  try {
    const importRows = db.transaction(() => {
      const existing = db.prepare(
        "SELECT id, remind_at, message, channel_id, author_id, silent FROM reminders WHERE id = ?",
      );
      for (const reminder of reminders) {
        const row = existing.get(reminder.id) as
          Record<string, unknown> | undefined;
        if (row && !sameReminder(row, reminder)) {
          throw new Error(
            `Destination reminder ID ${reminder.id} differs from the source`,
          );
        }
      }
      const insert = db.prepare(`
        INSERT OR IGNORE INTO reminders
          (id, remind_at, available_at, message, channel_id, author_id, silent, status, attempts)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', 0)
      `);
      for (const reminder of reminders) {
        insert.run(
          reminder.id,
          reminder.remindAt,
          reminder.remindAt,
          reminder.message,
          reminder.channelId,
          reminder.authorId,
          reminder.silent ? 1 : 0,
        );
      }
    });
    importRows();
    const imported = reminders.filter((reminder) =>
      db.prepare("SELECT 1 FROM reminders WHERE id = ?").get(reminder.id),
    ).length;
    if (imported !== reminders.length) {
      throw new Error(
        `SQLite verification failed: expected ${reminders.length}, found ${imported}`,
      );
    }
  } finally {
    db.close();
  }
}

async function importD1(reminders: SourceReminder[]): Promise<void> {
  const accountId = required("CLOUDFLARE_ACCOUNT_ID");
  const databaseId = required("D1_DATABASE_ID");
  const token = required("CLOUDFLARE_API_TOKEN");
  const query = async (sql: string, params: unknown[] = []) => {
    const response = await fetch(
      `https://api.cloudflare.com/client/v4/accounts/${accountId}/d1/database/${databaseId}/query`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ sql, params }),
      },
    );
    const body = (await response.json()) as {
      success: boolean;
      errors?: Array<{ message: string }>;
      result?: Array<{ results?: Array<Record<string, unknown>> }>;
    };
    if (!response.ok || !body.success) {
      throw new Error(
        `D1 query failed: ${body.errors?.map((error) => error.message).join(", ") ?? response.status}`,
      );
    }
    return body.result?.[0]?.results ?? [];
  };

  for (const reminder of reminders) {
    const existing = await query(
      "SELECT id, remind_at, message, channel_id, author_id, silent FROM reminders WHERE id = ?",
      [reminder.id],
    );
    if (existing.length && !sameReminder(existing[0], reminder)) {
      throw new Error(
        `Destination reminder ID ${reminder.id} differs from the source`,
      );
    }
  }
  for (const reminder of reminders) {
    await query(
      `INSERT OR IGNORE INTO reminders
        (id, remind_at, available_at, message, channel_id, author_id, silent, status, attempts)
       VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', 0)`,
      [
        reminder.id,
        reminder.remindAt,
        reminder.remindAt,
        reminder.message,
        reminder.channelId,
        reminder.authorId,
        reminder.silent ? 1 : 0,
      ],
    );
  }
  let imported = 0;
  for (const reminder of reminders) {
    imported += (
      await query("SELECT 1 FROM reminders WHERE id = ?", [reminder.id])
    ).length;
  }
  if (imported !== reminders.length) {
    throw new Error(
      `D1 verification failed: expected ${reminders.length}, found ${imported}`,
    );
  }
}

function required(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing ${name}`);
  }
  return value;
}

function sameReminder(
  row: Record<string, unknown>,
  reminder: SourceReminder,
): boolean {
  return (
    Number(row.id) === reminder.id &&
    Number(row.remind_at) === reminder.remindAt &&
    String(row.message) === reminder.message &&
    String(row.channel_id) === reminder.channelId &&
    String(row.author_id) === reminder.authorId &&
    Boolean(row.silent) === reminder.silent
  );
}
