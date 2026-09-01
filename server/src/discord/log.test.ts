import assert from "node:assert/strict";
import test from "node:test";
import { HTTPError } from "@discordjs/rest";
import { discordErrorMetadata } from "./client.js";

test("Discord error metadata redacts interaction webhook tokens", () => {
  const error = new HTTPError(
    404,
    "Not Found",
    "PATCH",
    "https://discord.com/api/v10/webhooks/12345678901234567/secret-token/messages/@original",
    { body: {}, files: [] },
  );
  assert.deepEqual(discordErrorMetadata(error), {
    status: 404,
    route:
      "/api/v10/webhooks/12345678901234567/[interaction-token]/messages/@original",
  });
});
