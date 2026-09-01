import assert from "node:assert/strict";
import test from "node:test";
import { MemoryStorage } from "./memory.js";

test("reminder storage claims, completes, and filters reminders", async () => {
  const storage = new MemoryStorage();
  const first = await storage.createReminder({
    remindAt: 100,
    message: "first",
    channelId: "1",
    authorId: "10",
    silent: false,
  });
  await storage.createReminder({
    remindAt: 200,
    message: "second",
    channelId: "2",
    authorId: "20",
    silent: true,
  });

  assert.equal((await storage.listReminders("10")).length, 1);
  const claimed = await storage.claimDueReminders(150, 1_000, 25);
  assert.deepEqual(
    claimed.map((reminder) => reminder.id),
    [first.id],
  );
  assert.equal(claimed[0].attempts, 1);
  assert.ok(claimed[0].leaseToken);
  assert.equal(
    await storage.completeReminder(first.id, claimed[0].leaseToken!),
    true,
  );
  assert.equal(await storage.getReminder(first.id), null);
  assert.equal(await storage.nextReminderAt(), 200);
});

test("expired leases can be reclaimed and failed reminders released", async () => {
  const storage = new MemoryStorage();
  const reminder = await storage.createReminder({
    remindAt: 100,
    message: "retry",
    channelId: "1",
    authorId: "10",
    silent: false,
  });
  const [firstClaim] = await storage.claimDueReminders(100, 200, 25);
  assert.equal((await storage.claimDueReminders(150, 300, 25)).length, 0);
  const [secondClaim] = await storage.claimDueReminders(200, 300, 25);
  assert.equal(secondClaim.id, reminder.id);
  assert.notEqual(secondClaim.leaseToken, firstClaim.leaseToken);
  assert.equal(
    await storage.releaseReminder(
      reminder.id,
      secondClaim.leaseToken!,
      400,
      "failed",
    ),
    true,
  );
  assert.equal(await storage.nextReminderAt(), 400);
});

test("temporary interaction state is owner-bound and consumed once", async () => {
  const storage = new MemoryStorage();
  await storage.createInteractionState({
    id: "state",
    kind: "manager_say",
    ownerUserId: "10",
    guildId: "20",
    channelId: "30",
    payload: { content: "test" },
    createdAt: 100,
    expiresAt: 200,
  });
  const lookup = {
    id: "state",
    kind: "manager_say",
    ownerUserId: "10",
    guildId: "20",
    channelId: "30",
    now: 150,
  };
  assert.equal(
    await storage.getInteractionState({ ...lookup, ownerUserId: "11" }),
    null,
  );
  assert.equal((await storage.consumeInteractionState(lookup))?.id, "state");
  assert.equal(await storage.consumeInteractionState(lookup), null);
});

test("interaction IDs are claimed once and cleaned after expiration", async () => {
  const storage = new MemoryStorage();
  assert.equal(await storage.claimInteraction("interaction", 200), true);
  assert.equal(await storage.claimInteraction("interaction", 200), false);
  assert.deepEqual(await storage.cleanupExpired(200), {
    interactionStates: 0,
    processedInteractions: 1,
  });
  assert.equal(await storage.claimInteraction("interaction", 300), true);
});
