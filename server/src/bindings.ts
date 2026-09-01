import type { AppEnv } from "./env.js";
import type { ReminderSchedulerService } from "./reminders/scheduler.js";
import type { Storage } from "./storage/types.js";

export interface BackgroundTasks {
  waitUntil(promise: Promise<unknown>): void;
}

export interface AppBindings {
  Variables: {
    env: AppEnv;
    storage: Storage;
    scheduler: ReminderSchedulerService;
    background: BackgroundTasks;
  };
}

export interface WorkerBindings {
  DB: D1Database;
  REMINDER_SCHEDULER: DurableObjectNamespace;
  DISCORD_APPLICATION_ID?: string;
  DISCORD_BOT_TOKEN?: string;
  DISCORD_TOKEN?: string;
  DISCORD_PUBLIC_KEY?: string;
  GUILD_IDS?: string;
  CTF_CATEGORY_CHANNELS?: string;
  CTF_ROLES?: string;
  UIUC_ROLES?: string;
  MODERATOR_ROLES?: string;
  PRIVATE_ROLES?: string;
  PORT?: string;
}
