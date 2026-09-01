import assert from "node:assert/strict";
import test from "node:test";
import { loadEnv } from "./env.js";

const base = {
  DISCORD_APPLICATION_ID: "12345678901234567",
  DISCORD_BOT_TOKEN: "token",
  DISCORD_PUBLIC_KEY: "00".repeat(32),
  GUILD_IDS: "12345678901234567",
};

test("private roles reject case-only duplicate names", () => {
  assert.throws(
    () =>
      loadEnv({
        ...base,
        PRIVATE_ROLES: JSON.stringify([
          { name: "Blue Team", discord_role_id: "12345678901234567" },
          { name: "blue team", discord_role_id: "22345678901234567" },
        ]),
      }),
    /ambiguous names/,
  );
});
