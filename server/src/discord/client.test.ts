import assert from "node:assert/strict";
import test from "node:test";
import type { AppEnv } from "../env.js";
import { listGuildRoles } from "./client.js";

test("Discord REST helpers use typed v10 routes through fetch", async () => {
  const originalFetch = globalThis.fetch;
  let requestedUrl = "";
  globalThis.fetch = (async (input) => {
    requestedUrl = String(input);
    return new Response(
      JSON.stringify([
        {
          id: "12345678901234567",
          name: "role",
          color: 0,
          colors: {
            primary_color: 0,
            secondary_color: null,
            tertiary_color: null,
          },
          hoist: false,
          icon: null,
          unicode_emoji: null,
          position: 1,
          permissions: "0",
          managed: false,
          mentionable: false,
          flags: 0,
        },
      ]),
      {
        headers: {
          "Content-Type": "application/json",
          "X-RateLimit-Bucket": "test",
          "X-RateLimit-Limit": "1",
          "X-RateLimit-Remaining": "1",
          "X-RateLimit-Reset-After": "1",
        },
      },
    );
  }) as typeof fetch;

  try {
    const roles = await listGuildRoles(
      {
        DISCORD_BOT_TOKEN: "discord-rest-client-test",
      } as AppEnv,
      "12345678901234567",
    );
    assert.equal(roles[0].name, "role");
    assert.equal(
      requestedUrl,
      "https://discord.com/api/v10/guilds/12345678901234567/roles",
    );
  } finally {
    globalThis.fetch = originalFetch;
  }
});
