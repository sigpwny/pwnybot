import { createChannelMessage, createDm } from "../discord/client.js";
import type { AppEnv } from "../env.js";
import type { Storage } from "../storage/types.js";
import { logError } from "../log.js";
import type { Reminder } from "../storage/types.js";

const CLAIM_LIMIT = 25;
const LEASE_MS = 60_000;
const MAX_RETRY_MS = 15 * 60_000;
const MAX_ATTEMPTS = 5;

function retryDelay(attempts: number): number {
  return Math.min(MAX_RETRY_MS, 5_000 * 2 ** Math.min(attempts - 1, 8));
}

type DeliverReminder = (reminder: Reminder, env: AppEnv) => Promise<void>;

async function sendReminder(reminder: Reminder, env: AppEnv): Promise<void> {
  const channelId = reminder.silent
    ? (await createDm(env, reminder.authorId)).id
    : reminder.channelId;
  await createChannelMessage(
    env,
    channelId,
    reminder.message,
    `pwr-${reminder.id}`,
  );
}

export async function deliverDueReminders(
  storage: Storage,
  env: AppEnv,
  now = Date.now(),
  deliver: DeliverReminder = sendReminder,
): Promise<number> {
  const reminders = await storage.claimDueReminders(
    now,
    now + LEASE_MS,
    CLAIM_LIMIT,
  );
  for (const reminder of reminders) {
    const leaseToken = reminder.leaseToken;
    if (!leaseToken) {
      continue;
    }

    try {
      await deliver(reminder, env);
      await storage.completeReminder(reminder.id, leaseToken);
    } catch (error) {
      if (reminder.attempts >= MAX_ATTEMPTS) {
        await storage.completeReminder(reminder.id, leaseToken);
        logError("reminder_abandoned", error, {
          reminder_id: reminder.id,
          attempts: reminder.attempts,
          channel_id: reminder.channelId,
          author_id: reminder.authorId,
          silent: reminder.silent,
        });
      } else {
        await storage.releaseReminder(
          reminder.id,
          leaseToken,
          Date.now() + retryDelay(reminder.attempts),
          error instanceof Error ? error.name : "unknown",
        );
        logError("reminder_delivery_failed", error, {
          reminder_id: reminder.id,
          attempts: reminder.attempts,
          channel_id: reminder.channelId,
          author_id: reminder.authorId,
          silent: reminder.silent,
        });
      }
    }
  }
  return reminders.length;
}
