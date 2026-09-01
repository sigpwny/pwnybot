import type {
  CleanupResult,
  InteractionState,
  InteractionStateLookup,
  NewReminder,
  Reminder,
  Storage,
} from "./types.js";

export class MemoryStorage implements Storage {
  private reminders: Reminder[] = [];
  private nextId = 1;
  private interactionStates = new Map<string, InteractionState>();
  private processedInteractions = new Map<string, number>();

  async createReminder(reminder: NewReminder): Promise<Reminder> {
    const created: Reminder = {
      ...reminder,
      id: this.nextId++,
      availableAt: reminder.remindAt,
      status: "pending",
      attempts: 0,
    };
    this.reminders.push(created);
    return { ...created };
  }

  async listReminders(authorId?: string): Promise<Reminder[]> {
    return this.reminders
      .filter((reminder) => !authorId || reminder.authorId === authorId)
      .sort((a, b) => a.remindAt - b.remindAt || a.id - b.id)
      .map((reminder) => ({ ...reminder }));
  }

  async getReminder(id: number): Promise<Reminder | null> {
    const reminder = this.reminders.find((candidate) => candidate.id === id);
    return reminder ? { ...reminder } : null;
  }

  async deleteReminder(id: number): Promise<boolean> {
    const length = this.reminders.length;
    this.reminders = this.reminders.filter((reminder) => reminder.id !== id);
    return this.reminders.length !== length;
  }

  async claimDueReminders(
    now: number,
    leaseUntil: number,
    limit: number,
  ): Promise<Reminder[]> {
    const leaseToken = crypto.randomUUID();
    const due = this.reminders
      .filter(
        (reminder) =>
          (reminder.status === "pending" && reminder.availableAt <= now) ||
          (reminder.status === "processing" &&
            (reminder.leaseUntil ?? 0) <= now),
      )
      .sort((a, b) => a.availableAt - b.availableAt || a.id - b.id)
      .slice(0, limit);
    for (const reminder of due) {
      reminder.status = "processing";
      reminder.leaseUntil = leaseUntil;
      reminder.leaseToken = leaseToken;
      reminder.attempts += 1;
    }
    return due.map((reminder) => ({ ...reminder }));
  }

  async completeReminder(id: number, leaseToken: string): Promise<boolean> {
    const reminder = this.reminders.find(
      (candidate) =>
        candidate.id === id &&
        candidate.status === "processing" &&
        candidate.leaseToken === leaseToken,
    );
    return reminder ? this.deleteReminder(id) : false;
  }

  async releaseReminder(
    id: number,
    leaseToken: string,
    availableAt: number,
    error: string,
  ): Promise<boolean> {
    const reminder = this.reminders.find(
      (candidate) =>
        candidate.id === id &&
        candidate.status === "processing" &&
        candidate.leaseToken === leaseToken,
    );
    if (!reminder) {
      return false;
    }
    reminder.status = "pending";
    reminder.availableAt = availableAt;
    reminder.leaseUntil = undefined;
    reminder.leaseToken = undefined;
    reminder.lastError = error;
    return true;
  }

  async nextReminderAt(): Promise<number | null> {
    if (this.reminders.length === 0) {
      return null;
    }
    return Math.min(
      ...this.reminders.map((reminder) =>
        reminder.status === "processing"
          ? (reminder.leaseUntil ?? reminder.availableAt)
          : reminder.availableAt,
      ),
    );
  }

  async createInteractionState(state: InteractionState): Promise<void> {
    if (this.interactionStates.has(state.id)) {
      return;
    }
    this.interactionStates.set(state.id, structuredClone(state));
  }

  async getInteractionState(
    lookup: InteractionStateLookup,
  ): Promise<InteractionState | null> {
    const state = this.interactionStates.get(lookup.id);
    return state && this.matchesState(state, lookup)
      ? structuredClone(state)
      : null;
  }

  async consumeInteractionState(
    lookup: InteractionStateLookup,
  ): Promise<InteractionState | null> {
    const state = this.interactionStates.get(lookup.id);
    if (!state || !this.matchesState(state, lookup)) {
      return null;
    }
    state.consumedAt = lookup.now;
    return structuredClone(state);
  }

  async claimInteraction(id: string, expiresAt: number): Promise<boolean> {
    if (this.processedInteractions.has(id)) {
      return false;
    }
    this.processedInteractions.set(id, expiresAt);
    return true;
  }

  async cleanupExpired(now: number): Promise<CleanupResult> {
    let interactionStates = 0;
    let processedInteractions = 0;
    for (const [id, state] of this.interactionStates) {
      if (state.expiresAt <= now) {
        this.interactionStates.delete(id);
        interactionStates += 1;
      }
    }
    for (const [id, expiresAt] of this.processedInteractions) {
      if (expiresAt <= now) {
        this.processedInteractions.delete(id);
        processedInteractions += 1;
      }
    }
    return { interactionStates, processedInteractions };
  }

  private matchesState(
    state: InteractionState,
    lookup: InteractionStateLookup,
  ): boolean {
    return (
      state.kind === lookup.kind &&
      state.ownerUserId === lookup.ownerUserId &&
      state.guildId === lookup.guildId &&
      state.channelId === lookup.channelId &&
      state.consumedAt === undefined &&
      state.expiresAt > lookup.now
    );
  }
}
