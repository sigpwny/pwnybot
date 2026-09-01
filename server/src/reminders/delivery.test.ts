import assert from "node:assert/strict";
import test from "node:test";
import type { AppEnv } from "../env.js";
import { MemoryStorage } from "../storage/memory.js";
import { deliverDueReminders } from "./delivery.js";

const env = {} as AppEnv;

test("failed reminders are deleted after five delivery attempts", async () => {
  const storage = new MemoryStorage();
  const reminder = await storage.createReminder({
    remindAt: 100,
    message: "test",
    channelId: "1",
    authorId: "2",
    silent: false,
  });
  const fail = async () => {
    throw new Error("delivery failed");
  };

  for (let attempt = 0; attempt < 5; attempt += 1) {
    await deliverDueReminders(storage, env, Number.MAX_SAFE_INTEGER, fail);
  }
  assert.equal(await storage.getReminder(reminder.id), null);
});
