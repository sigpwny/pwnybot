import assert from "node:assert/strict";
import test from "node:test";
import nacl from "tweetnacl";
import type { CommandRuntime } from "../commands/types.js";
import type { AppEnv } from "../env.js";
import { MemoryStorage } from "../storage/memory.js";
import { handleDiscordInteraction } from "./interactions.js";

function hex(value: Uint8Array): string {
  return Array.from(value, (byte) => byte.toString(16).padStart(2, "0")).join(
    "",
  );
}

const keyPair = nacl.sign.keyPair();
const env: AppEnv = {
  DISCORD_APPLICATION_ID: "12345678901234567",
  DISCORD_BOT_TOKEN: "token",
  DISCORD_PUBLIC_KEY: hex(keyPair.publicKey),
  GUILD_IDS: ["12345678901234567"],
  CTF_CATEGORY_CHANNELS: [],
  CTF_ROLES: [],
  UIUC_ROLES: [],
  MODERATOR_ROLES: [],
  PRIVATE_ROLES: [],
  PORT: 8787,
};
const runtime: CommandRuntime = {
  env,
  storage: new MemoryStorage(),
  scheduler: {
    schedule: async () => undefined,
    reconcile: async () => undefined,
  },
  background: { waitUntil: () => undefined },
};

function signedRequest(body: string): Request {
  const timestamp = String(Math.floor(Date.now() / 1_000));
  const signature = nacl.sign.detached(
    new TextEncoder().encode(timestamp + body),
    keyPair.secretKey,
  );
  return new Request("https://example.com/api/discord/interactions/callback", {
    method: "POST",
    headers: {
      "X-Signature-Ed25519": hex(signature),
      "X-Signature-Timestamp": timestamp,
    },
    body,
  });
}

test("signed Discord ping receives a pong", async () => {
  const response = await handleDiscordInteraction(
    env,
    runtime,
    signedRequest('{"type":1}'),
  );
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { type: 1 });
});

test("invalid Discord signatures are rejected", async () => {
  const request = signedRequest('{"type":1}');
  request.headers.set("X-Signature-Ed25519", "00".repeat(64));
  const response = await handleDiscordInteraction(env, runtime, request);
  assert.equal(response.status, 401);
});
