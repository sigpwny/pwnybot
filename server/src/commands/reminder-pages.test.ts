import assert from "node:assert/strict";
import test from "node:test";
import { renderReminderPage } from "./reminders.js";

test("reminder pages stay within Discord embed limits", () => {
  const reminders = Array.from({ length: 21 }, (_, index) => ({
    id: index + 1,
    remindAt: index,
    availableAt: index,
    message: `Reminder ${index}`,
    channelId: "1",
    authorId: "2",
    silent: false,
    status: "pending" as const,
    attempts: 0,
  }));
  const page = renderReminderPage(reminders, 1, "state");
  const embed = page.embeds[0];
  assert.ok(embed.description.length <= 3_900);
  assert.equal(embed.footer.text, "Page 2 of 3");
  assert.equal(page.components.length, 1);
});
