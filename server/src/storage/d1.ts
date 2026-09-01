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

export class D1Storage implements Storage {
  constructor(private readonly db: D1Database) {}

  async createReminder(reminder: NewReminder): Promise<Reminder> {
    const result = await this.db
      .prepare(
        `
        INSERT INTO reminders (remind_at, available_at, message, channel_id, author_id, silent)
        VALUES (?, ?, ?, ?, ?, ?)
      `,
      )
      .bind(
        reminder.remindAt,
        reminder.remindAt,
        reminder.message,
        reminder.channelId,
        reminder.authorId,
        reminder.silent ? 1 : 0,
      )
      .run();

    const id = Number(result.meta.last_row_id);
    const created = await this.getReminder(id);
    if (!created) {
      throw new Error("Failed to read newly created reminder");
    }
    return created;
  }

  async listReminders(authorId?: string): Promise<Reminder[]> {
    const statement = authorId
      ? this.db
          .prepare(
            "SELECT * FROM reminders WHERE author_id = ? ORDER BY remind_at, id",
          )
          .bind(authorId)
      : this.db.prepare("SELECT * FROM reminders ORDER BY remind_at, id");
    const result = await statement.all<Record<string, unknown>>();
    return result.results.map(reminderFromRow);
  }

  async getReminder(id: number): Promise<Reminder | null> {
    const row = await this.db
      .prepare("SELECT * FROM reminders WHERE id = ?")
      .bind(id)
      .first<Record<string, unknown>>();
    return row ? reminderFromRow(row) : null;
  }

  async deleteReminder(id: number): Promise<boolean> {
    const result = await this.db
      .prepare("DELETE FROM reminders WHERE id = ?")
      .bind(id)
      .run();
    return Boolean(result.meta.changes);
  }

  async claimDueReminders(
    now: number,
    leaseUntil: number,
    limit: number,
  ): Promise<Reminder[]> {
    const candidates = await this.db
      .prepare(
        `
        SELECT id FROM reminders
        WHERE (status = 'pending' AND available_at <= ?)
           OR (status = 'processing' AND lease_until <= ?)
        ORDER BY available_at, id
        LIMIT ?
      `,
      )
      .bind(now, now, limit)
      .all<{ id: number }>();

    if (candidates.results.length === 0) {
      return [];
    }

    const leaseToken = crypto.randomUUID();
    await this.db.batch(
      candidates.results.map(({ id }) =>
        this.db
          .prepare(
            `
            UPDATE reminders
            SET status = 'processing', lease_until = ?, lease_token = ?, attempts = attempts + 1
            WHERE id = ?
              AND ((status = 'pending' AND available_at <= ?)
                OR (status = 'processing' AND lease_until <= ?))
          `,
          )
          .bind(leaseUntil, leaseToken, id, now, now),
      ),
    );

    const claimed = await this.db
      .prepare(
        "SELECT * FROM reminders WHERE lease_token = ? ORDER BY available_at, id",
      )
      .bind(leaseToken)
      .all<Record<string, unknown>>();
    return claimed.results.map(reminderFromRow);
  }

  async completeReminder(id: number, leaseToken: string): Promise<boolean> {
    const result = await this.db
      .prepare(
        "DELETE FROM reminders WHERE id = ? AND status = 'processing' AND lease_token = ?",
      )
      .bind(id, leaseToken)
      .run();
    return Boolean(result.meta.changes);
  }

  async releaseReminder(
    id: number,
    leaseToken: string,
    availableAt: number,
    error: string,
  ): Promise<boolean> {
    const result = await this.db
      .prepare(
        `
        UPDATE reminders
        SET status = 'pending', available_at = ?, lease_until = NULL, lease_token = NULL, last_error = ?
        WHERE id = ? AND status = 'processing' AND lease_token = ?
      `,
      )
      .bind(availableAt, error, id, leaseToken)
      .run();
    return Boolean(result.meta.changes);
  }

  async nextReminderAt(): Promise<number | null> {
    const row = await this.db
      .prepare(
        `
        SELECT MIN(CASE WHEN status = 'processing' THEN lease_until ELSE available_at END) AS next_at
        FROM reminders
      `,
      )
      .first<{ next_at: number | null }>();
    return row?.next_at === null || row?.next_at === undefined
      ? null
      : Number(row.next_at);
  }

  async createInteractionState(state: InteractionState): Promise<void> {
    await this.db
      .prepare(
        `
        INSERT OR IGNORE INTO interaction_states
          (id, kind, owner_user_id, guild_id, channel_id, payload, created_at, expires_at, consumed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      `,
      )
      .bind(
        state.id,
        state.kind,
        state.ownerUserId,
        state.guildId,
        state.channelId,
        JSON.stringify(state.payload),
        state.createdAt,
        state.expiresAt,
        state.consumedAt ?? null,
      )
      .run();
  }

  async getInteractionState(
    lookup: InteractionStateLookup,
  ): Promise<InteractionState | null> {
    const row = await this.db
      .prepare(
        `
        SELECT * FROM interaction_states
        WHERE id = ? AND kind = ? AND owner_user_id = ? AND guild_id = ?
          AND channel_id = ? AND consumed_at IS NULL AND expires_at > ?
      `,
      )
      .bind(
        lookup.id,
        lookup.kind,
        lookup.ownerUserId,
        lookup.guildId,
        lookup.channelId,
        lookup.now,
      )
      .first<Record<string, unknown>>();
    return row ? interactionStateFromRow(row) : null;
  }

  async consumeInteractionState(
    lookup: InteractionStateLookup,
  ): Promise<InteractionState | null> {
    const result = await this.db
      .prepare(
        `
        UPDATE interaction_states SET consumed_at = ?
        WHERE id = ? AND kind = ? AND owner_user_id = ? AND guild_id = ?
          AND channel_id = ? AND consumed_at IS NULL AND expires_at > ?
      `,
      )
      .bind(
        lookup.now,
        lookup.id,
        lookup.kind,
        lookup.ownerUserId,
        lookup.guildId,
        lookup.channelId,
        lookup.now,
      )
      .run();
    if (!result.meta.changes) {
      return null;
    }
    const row = await this.db
      .prepare("SELECT * FROM interaction_states WHERE id = ?")
      .bind(lookup.id)
      .first<Record<string, unknown>>();
    return row ? interactionStateFromRow(row) : null;
  }

  async claimInteraction(id: string, expiresAt: number): Promise<boolean> {
    const result = await this.db
      .prepare(
        "INSERT OR IGNORE INTO processed_interactions (id, expires_at) VALUES (?, ?)",
      )
      .bind(id, expiresAt)
      .run();
    return Boolean(result.meta.changes);
  }

  async cleanupExpired(now: number): Promise<CleanupResult> {
    const [interactionStates, processedInteractions] = await this.db.batch([
      this.db
        .prepare("DELETE FROM interaction_states WHERE expires_at <= ?")
        .bind(now),
      this.db
        .prepare("DELETE FROM processed_interactions WHERE expires_at <= ?")
        .bind(now),
    ]);
    return {
      interactionStates: interactionStates.meta.changes ?? 0,
      processedInteractions: processedInteractions.meta.changes ?? 0,
    };
  }
}
