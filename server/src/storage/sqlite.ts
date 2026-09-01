import { mkdirSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import Database from "better-sqlite3";
import {
  interactionStateFromRow,
  reminderFromRow,
  type CleanupResult,
  type InteractionState,
  type InteractionStateLookup,
  type NewReminder,
  type Reminder,
  type Storage,
} from "./types.js";

export class SqliteStorage implements Storage {
  private readonly db: Database.Database;

  constructor(path = "data/local.sqlite") {
    mkdirSync(dirname(path), { recursive: true });
    this.db = new Database(path);
    this.db.pragma("journal_mode = WAL");
    this.db.pragma("foreign_keys = ON");
  }

  migrate(migrationsPath = "migrations"): void {
    this.db.exec(
      "CREATE TABLE IF NOT EXISTS __migrations (name TEXT PRIMARY KEY, applied_at INTEGER NOT NULL)",
    );
    const applyMigration = this.db.transaction((name: string, sql: string) => {
      this.db.exec(sql);
      this.db
        .prepare("INSERT INTO __migrations (name, applied_at) VALUES (?, ?)")
        .run(name, Date.now());
    });

    for (const name of readdirSync(resolve(migrationsPath))
      .filter((entry) => entry.endsWith(".sql"))
      .sort()) {
      if (
        this.db.prepare("SELECT 1 FROM __migrations WHERE name = ?").get(name)
      ) {
        continue;
      }
      applyMigration(
        name,
        readFileSync(join(resolve(migrationsPath), name), "utf8"),
      );
    }
  }

  async createReminder(reminder: NewReminder): Promise<Reminder> {
    const result = this.db
      .prepare(
        `
        INSERT INTO reminders (remind_at, available_at, message, channel_id, author_id, silent)
        VALUES (?, ?, ?, ?, ?, ?)
      `,
      )
      .run(
        reminder.remindAt,
        reminder.remindAt,
        reminder.message,
        reminder.channelId,
        reminder.authorId,
        reminder.silent ? 1 : 0,
      );
    const created = await this.getReminder(Number(result.lastInsertRowid));
    if (!created) {
      throw new Error("Failed to read newly created reminder");
    }
    return created;
  }

  async listReminders(authorId?: string): Promise<Reminder[]> {
    const rows = authorId
      ? this.db
          .prepare(
            "SELECT * FROM reminders WHERE author_id = ? ORDER BY remind_at, id",
          )
          .all(authorId)
      : this.db.prepare("SELECT * FROM reminders ORDER BY remind_at, id").all();
    return (rows as Record<string, unknown>[]).map(reminderFromRow);
  }

  async getReminder(id: number): Promise<Reminder | null> {
    const row = this.db
      .prepare("SELECT * FROM reminders WHERE id = ?")
      .get(id) as Record<string, unknown> | undefined;
    return row ? reminderFromRow(row) : null;
  }

  async deleteReminder(id: number): Promise<boolean> {
    return Boolean(
      this.db.prepare("DELETE FROM reminders WHERE id = ?").run(id).changes,
    );
  }

  async claimDueReminders(
    now: number,
    leaseUntil: number,
    limit: number,
  ): Promise<Reminder[]> {
    const claim = this.db.transaction(() => {
      const candidates = this.db
        .prepare(
          `
          SELECT id FROM reminders
          WHERE (status = 'pending' AND available_at <= ?)
             OR (status = 'processing' AND lease_until <= ?)
          ORDER BY available_at, id
          LIMIT ?
        `,
        )
        .all(now, now, limit) as Array<{ id: number }>;
      if (candidates.length === 0) {
        return [];
      }

      const leaseToken = crypto.randomUUID();
      const update = this.db.prepare(`
        UPDATE reminders
        SET status = 'processing', lease_until = ?, lease_token = ?, attempts = attempts + 1
        WHERE id = ?
          AND ((status = 'pending' AND available_at <= ?)
            OR (status = 'processing' AND lease_until <= ?))
      `);
      for (const { id } of candidates) {
        update.run(leaseUntil, leaseToken, id, now, now);
      }
      return this.db
        .prepare(
          "SELECT * FROM reminders WHERE lease_token = ? ORDER BY available_at, id",
        )
        .all(leaseToken);
    });

    return (claim() as Record<string, unknown>[]).map(reminderFromRow);
  }

  async completeReminder(id: number, leaseToken: string): Promise<boolean> {
    return Boolean(
      this.db
        .prepare(
          "DELETE FROM reminders WHERE id = ? AND status = 'processing' AND lease_token = ?",
        )
        .run(id, leaseToken).changes,
    );
  }

  async releaseReminder(
    id: number,
    leaseToken: string,
    availableAt: number,
    error: string,
  ): Promise<boolean> {
    return Boolean(
      this.db
        .prepare(
          `
          UPDATE reminders
          SET status = 'pending', available_at = ?, lease_until = NULL, lease_token = NULL, last_error = ?
          WHERE id = ? AND status = 'processing' AND lease_token = ?
        `,
        )
        .run(availableAt, error, id, leaseToken).changes,
    );
  }

  async nextReminderAt(): Promise<number | null> {
    const row = this.db
      .prepare(
        `
        SELECT MIN(CASE WHEN status = 'processing' THEN lease_until ELSE available_at END) AS next_at
        FROM reminders
      `,
      )
      .get() as { next_at: number | null };
    return row.next_at === null ? null : Number(row.next_at);
  }

  async createInteractionState(state: InteractionState): Promise<void> {
    this.db
      .prepare(
        `
        INSERT OR IGNORE INTO interaction_states
          (id, kind, owner_user_id, guild_id, channel_id, payload, created_at, expires_at, consumed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      `,
      )
      .run(
        state.id,
        state.kind,
        state.ownerUserId,
        state.guildId,
        state.channelId,
        JSON.stringify(state.payload),
        state.createdAt,
        state.expiresAt,
        state.consumedAt ?? null,
      );
  }

  async getInteractionState(
    lookup: InteractionStateLookup,
  ): Promise<InteractionState | null> {
    const row = this.db
      .prepare(
        `
        SELECT * FROM interaction_states
        WHERE id = ? AND kind = ? AND owner_user_id = ? AND guild_id = ?
          AND channel_id = ? AND consumed_at IS NULL AND expires_at > ?
      `,
      )
      .get(
        lookup.id,
        lookup.kind,
        lookup.ownerUserId,
        lookup.guildId,
        lookup.channelId,
        lookup.now,
      ) as Record<string, unknown> | undefined;
    return row ? interactionStateFromRow(row) : null;
  }

  async consumeInteractionState(
    lookup: InteractionStateLookup,
  ): Promise<InteractionState | null> {
    const consume = this.db.transaction(() => {
      const result = this.db
        .prepare(
          `
          UPDATE interaction_states SET consumed_at = ?
          WHERE id = ? AND kind = ? AND owner_user_id = ? AND guild_id = ?
            AND channel_id = ? AND consumed_at IS NULL AND expires_at > ?
        `,
        )
        .run(
          lookup.now,
          lookup.id,
          lookup.kind,
          lookup.ownerUserId,
          lookup.guildId,
          lookup.channelId,
          lookup.now,
        );
      if (!result.changes) {
        return undefined;
      }
      return this.db
        .prepare("SELECT * FROM interaction_states WHERE id = ?")
        .get(lookup.id) as Record<string, unknown>;
    });
    const row = consume();
    return row ? interactionStateFromRow(row) : null;
  }

  async claimInteraction(id: string, expiresAt: number): Promise<boolean> {
    return Boolean(
      this.db
        .prepare(
          "INSERT OR IGNORE INTO processed_interactions (id, expires_at) VALUES (?, ?)",
        )
        .run(id, expiresAt).changes,
    );
  }

  async cleanupExpired(now: number): Promise<CleanupResult> {
    const cleanup = this.db.transaction(() => ({
      interactionStates: this.db
        .prepare("DELETE FROM interaction_states WHERE expires_at <= ?")
        .run(now).changes,
      processedInteractions: this.db
        .prepare("DELETE FROM processed_interactions WHERE expires_at <= ?")
        .run(now).changes,
    }));
    return cleanup();
  }
}
