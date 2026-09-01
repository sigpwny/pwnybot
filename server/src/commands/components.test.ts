import assert from "node:assert/strict";
import test from "node:test";
import { InteractionType } from "discord-api-types/v10";
import type { AppEnv } from "../env.js";
import { MemoryStorage } from "../storage/memory.js";
import { dispatchComponent } from "./components.js";
import type { CommandRuntime } from "./types.js";

test("manager say confirmations are owner-bound", async () => {
  const storage = new MemoryStorage();
  await storage.createInteractionState({
    id: "state",
    kind: "manager_say",
    ownerUserId: "10",
    guildId: "20",
    channelId: "30",
    payload: { targetChannelId: "40", content: "hello" },
    createdAt: Date.now(),
    expiresAt: Date.now() + 60_000,
  });
  const runtime: CommandRuntime = {
    env: {
      DISCORD_APPLICATION_ID: "12345678901234567",
      DISCORD_BOT_TOKEN: "token",
    } as AppEnv,
    storage,
    scheduler: {
      schedule: async () => undefined,
      reconcile: async () => undefined,
    },
    background: { waitUntil: () => undefined },
  };
  const response = await dispatchComponent(
    {
      id: "interaction",
      application_id: "12345678901234567",
      token: "token",
      type: InteractionType.MessageComponent,
      guild_id: "20",
      channel_id: "30",
      member: { user: { id: "11", username: "other" }, roles: [] },
      data: { custom_id: "manager-say:confirm:state" },
    },
    runtime,
  );
  assert.equal(response.status, 200);
  assert.ok(
    await storage.getInteractionState({
      id: "state",
      kind: "manager_say",
      ownerUserId: "10",
      guildId: "20",
      channelId: "30",
      now: Date.now(),
    }),
  );
});
