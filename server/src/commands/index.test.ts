import assert from "node:assert/strict";
import test from "node:test";
import { commandPayloads } from "./index.js";

test("the command manifest includes restored HTTP-native manager commands", () => {
  assert.deepEqual(
    commandPayloads.map((command) => command.name),
    [
      "reverserepeat",
      "template",
      "chal",
      "ctf",
      "ctfs",
      "roles",
      "manager",
      "copypasta",
      "reminders",
    ],
  );

  const manager = commandPayloads.find((command) => command.name === "manager");
  const options = manager?.options as Array<{ name: string }>;
  assert.deepEqual(
    options.map((option) => option.name),
    ["say", "edit", "assign_roles"],
  );
});
