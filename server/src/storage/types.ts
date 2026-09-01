export interface Reminder {
  id: number;
  remindAt: number;
  availableAt: number;
  message: string;
  channelId: string;
  authorId: string;
  silent: boolean;
  status: "pending" | "processing";
  leaseUntil?: number;
  leaseToken?: string;
  attempts: number;
  lastError?: string;
}

export interface NewReminder {
  remindAt: number;
  message: string;
  channelId: string;
  authorId: string;
  silent: boolean;
}

export interface InteractionState {
  id: string;
  kind: string;
  ownerUserId: string;
  guildId: string;
  channelId: string;
  payload: Record<string, unknown>;
  createdAt: number;
  expiresAt: number;
  consumedAt?: number;
}

export interface InteractionStateLookup {
  id: string;
  kind: string;
  ownerUserId: string;
  guildId: string;
  channelId: string;
  now: number;
}

export interface CleanupResult {
  interactionStates: number;
  processedInteractions: number;
}

export interface Storage {
  createReminder(reminder: NewReminder): Promise<Reminder>;
  listReminders(authorId?: string): Promise<Reminder[]>;
  getReminder(id: number): Promise<Reminder | null>;
  deleteReminder(id: number): Promise<boolean>;
  claimDueReminders(
    now: number,
    leaseUntil: number,
    limit: number,
  ): Promise<Reminder[]>;
  completeReminder(id: number, leaseToken: string): Promise<boolean>;
  releaseReminder(
    id: number,
    leaseToken: string,
    availableAt: number,
    error: string,
  ): Promise<boolean>;
  nextReminderAt(): Promise<number | null>;
  createInteractionState(state: InteractionState): Promise<void>;
  getInteractionState(
    lookup: InteractionStateLookup,
  ): Promise<InteractionState | null>;
  consumeInteractionState(
    lookup: InteractionStateLookup,
  ): Promise<InteractionState | null>;
  claimInteraction(id: string, expiresAt: number): Promise<boolean>;
  cleanupExpired(now: number): Promise<CleanupResult>;
}

export function reminderFromRow(row: Record<string, unknown>): Reminder {
  return {
    id: Number(row.id),
    remindAt: Number(row.remind_at),
    availableAt: Number(row.available_at),
    message: String(row.message),
    channelId: String(row.channel_id),
    authorId: String(row.author_id),
    silent: Boolean(row.silent),
    status: row.status === "processing" ? "processing" : "pending",
    leaseUntil:
      row.lease_until === null || row.lease_until === undefined
        ? undefined
        : Number(row.lease_until),
    leaseToken:
      row.lease_token === null || row.lease_token === undefined
        ? undefined
        : String(row.lease_token),
    attempts: Number(row.attempts),
    lastError:
      row.last_error === null || row.last_error === undefined
        ? undefined
        : String(row.last_error),
  };
}

export function interactionStateFromRow(
  row: Record<string, unknown>,
): InteractionState {
  return {
    id: String(row.id),
    kind: String(row.kind),
    ownerUserId: String(row.owner_user_id),
    guildId: String(row.guild_id),
    channelId: String(row.channel_id),
    payload: JSON.parse(String(row.payload)) as Record<string, unknown>,
    createdAt: Number(row.created_at),
    expiresAt: Number(row.expires_at),
    consumedAt:
      row.consumed_at === null || row.consumed_at === undefined
        ? undefined
        : Number(row.consumed_at),
  };
}
