import { serve } from "@hono/node-server";
import dotenv from "dotenv";
import { createApp } from "./app.js";
import { loadEnv } from "./env.js";
import { TimerReminderScheduler } from "./reminders/scheduler.js";
import { SqliteStorage } from "./storage/sqlite.js";
import { logError } from "./log.js";

dotenv.config({ path: "../.env" });
dotenv.config({ path: ".env", override: false });

const env = loadEnv(process.env);
const storage = new SqliteStorage(
  process.env.SQLITE_PATH ?? "data/local.sqlite",
);
storage.migrate(process.env.MIGRATIONS_PATH ?? "migrations");
const scheduler = new TimerReminderScheduler(storage, env);
await scheduler.reconcile();
await storage.cleanupExpired(Date.now());
setInterval(() => {
  void storage.cleanupExpired(Date.now());
}, 15 * 60_000).unref();

const app = createApp(env, storage, scheduler, {
  waitUntil(promise) {
    void promise.catch((error) => logError("background_task_failed", error));
  },
});

serve({ fetch: app.fetch, port: env.PORT }, () => {
  console.log(`pwnybot listening on http://localhost:${env.PORT}`);
});
