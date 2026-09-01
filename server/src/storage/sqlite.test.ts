import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { SqliteStorage } from "./sqlite.js";

test("SQLite applies migrations and implements reminder leases", async () => {
  const directory = mkdtempSync(join(tmpdir(), "pwnybot-sqlite-"));
  try {
    const storage = new SqliteStorage(join(directory, "test.sqlite"));
    storage.migrate("migrations");
    const reminder = await storage.createReminder({
      remindAt: 100,
      message: "test",
      channelId: "1",
      authorId: "2",
      silent: false,
    });
    const [claimed] = await storage.claimDueReminders(100, 200, 1);
    assert.equal(claimed.id, reminder.id);
    assert.equal(claimed.attempts, 1);
    assert.ok(claimed.leaseToken);
    assert.equal(
      await storage.completeReminder(reminder.id, claimed.leaseToken!),
      true,
    );
    assert.equal(await storage.nextReminderAt(), null);

    await storage.createInteractionState({
      id: "state",
      kind: "test",
      ownerUserId: "1",
      guildId: "2",
      channelId: "3",
      payload: { value: true },
      createdAt: 100,
      expiresAt: 200,
    });
    const lookup = {
      id: "state",
      kind: "test",
      ownerUserId: "1",
      guildId: "2",
      channelId: "3",
      now: 150,
    };
    assert.equal((await storage.consumeInteractionState(lookup))?.id, "state");
    assert.equal(await storage.consumeInteractionState(lookup), null);
    assert.equal(await storage.claimInteraction("interaction", 200), true);
    assert.equal(await storage.claimInteraction("interaction", 200), false);
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});
