import {
  ApplicationCommandOptionType,
  ApplicationCommandType,
  ButtonStyle,
  ComponentType,
} from "discord-api-types/v10";
import { message } from "../discord/responses.js";
import type { Reminder } from "../storage/types.js";
import type { InteractionMessageData } from "../discord/types.js";
import { logError } from "../log.js";
import {
  deferredTask,
  finish,
  hasAdministrator,
  hasAnyRole,
} from "./helpers.js";
import {
  booleanOption,
  integerOption,
  option,
  stringOption,
  subcommand,
  userId,
} from "./options.js";
import type { CommandDefinition } from "./types.js";

const DURATION = /^(?:(\d+)w)?(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?$/;
const PAGE_SIZE = 10;
const PAGE_DESCRIPTION_LIMIT = 3_900;
const PAGE_TTL_MS = 15 * 60_000;

export function parseDuration(value: string): number | null {
  const match = DURATION.exec(value);
  if (!match) {
    return null;
  }
  const [weeks, days, hours, minutes, seconds] = match
    .slice(1)
    .map((part) => Number(part || 0));
  const duration =
    ((((weeks * 7 + days) * 24 + hours) * 60 + minutes) * 60 + seconds) * 1_000;
  return Number.isSafeInteger(duration) ? duration : null;
}

export function renderReminderPage(
  reminders: Reminder[],
  requestedPage: number,
  stateId: string,
  title?: string,
): InteractionMessageData {
  const pages: string[][] = [[]];
  for (const reminder of reminders) {
    const line = `${reminder.id}: ${reminder.silent ? "dm" : `<#${reminder.channelId}>`}: '${reminder.message}' <t:${Math.floor(reminder.remindAt / 1_000)}:R>`;
    const current = pages.at(-1)!;
    const nextLength =
      current.join("\n").length + (current.length ? 1 : 0) + line.length;
    if (
      current.length > 0 &&
      (current.length >= PAGE_SIZE || nextLength > PAGE_DESCRIPTION_LIMIT)
    ) {
      pages.push([line]);
    } else {
      current.push(line);
    }
  }
  const pageCount = pages.length;
  const page = Math.min(Math.max(0, requestedPage), pageCount - 1);
  const description = pages[page].join("\n");
  return {
    embeds: [
      {
        ...(title ? { title } : {}),
        description:
          description || "There are no reminders currently for this query",
        footer: { text: `Page ${page + 1} of ${pageCount}` },
      },
    ],
    components:
      pageCount > 1
        ? [
            {
              type: ComponentType.ActionRow,
              components: [
                {
                  type: ComponentType.Button,
                  style: ButtonStyle.Secondary,
                  label: "Previous",
                  custom_id: `reminders-page:${stateId}:${page - 1}`,
                  disabled: page === 0,
                },
                {
                  type: ComponentType.Button,
                  style: ButtonStyle.Secondary,
                  label: "Next",
                  custom_id: `reminders-page:${stateId}:${page + 1}`,
                  disabled: page === pageCount - 1,
                },
              ],
            },
          ]
        : [],
  };
}

export const remindersCommand: CommandDefinition = {
  command: {
    name: "reminders",
    type: ApplicationCommandType.ChatInput,
    description: "No Description Set",
    options: [
      {
        type: ApplicationCommandOptionType.Subcommand,
        name: "create",
        description: "Create a reminder",
        options: [
          {
            type: ApplicationCommandOptionType.String,
            name: "when",
            description:
              "When the reminer should be triggered. Format: (1w2d3h4m5s)",
            required: true,
          },
          {
            type: ApplicationCommandOptionType.String,
            name: "message",
            description: "What message should be attached to the reminder?",
            required: true,
            max_length: 1900,
          },
          {
            type: ApplicationCommandOptionType.Boolean,
            name: "silent",
            description: "Should the reminder be dmed?",
            required: false,
          },
        ],
      },
      {
        type: ApplicationCommandOptionType.Subcommand,
        name: "list",
        description:
          "List the scheduled reminders for all users or a particular user",
        options: [
          {
            type: ApplicationCommandOptionType.User,
            name: "user",
            description:
              "User whose reminders you would like to view, default is all users.",
            required: false,
          },
        ],
      },
      {
        type: ApplicationCommandOptionType.Subcommand,
        name: "delete",
        description: "Delete a reminder by its ID",
        options: [
          {
            type: ApplicationCommandOptionType.Integer,
            name: "reminder_id",
            description: "The ID of the reminder to delete",
            required: true,
          },
        ],
      },
    ],
  },
  async handle(interaction, runtime) {
    if (
      !hasAnyRole(interaction, runtime.env.MODERATOR_ROLES) &&
      !hasAdministrator(interaction)
    ) {
      return message("You do not have permission to use this command.", true);
    }

    const action = subcommand(interaction)?.name;
    const authorId = userId(interaction);
    if (action === "create") {
      const duration = parseDuration(stringOption(interaction, "when"));
      if (duration === null || duration <= 0) {
        return message(
          "Invalid time format. Please use something like '1w2d3h4m5s'.",
          true,
        );
      }
      const remindAt = Date.now() + duration;
      const reminderMessage = `Reminder for <@${authorId}>: ${stringOption(interaction, "message")}`;
      if (reminderMessage.length > 2_000) {
        return message("Reminder message is too long.", true);
      }
      return deferredTask(interaction, runtime, true, async () => {
        await runtime.storage.createReminder({
          remindAt,
          message: reminderMessage,
          channelId: interaction.channel_id ?? "",
          authorId,
          silent: booleanOption(interaction, "silent"),
        });
        await runtime.scheduler.schedule(remindAt).catch((error) =>
          logError("reminder_schedule_failed", error, {
            interaction_id: interaction.id,
            guild_id: interaction.guild_id,
            author_id: authorId,
          }),
        );
        await finish(interaction, runtime, "Reminder is queued!");
      });
    }

    if (action === "list") {
      const requestedUserId = option(interaction, "user")?.value;
      return deferredTask(interaction, runtime, true, async () => {
        const filterAuthorId =
          typeof requestedUserId === "string" ? requestedUserId : undefined;
        const reminders = await runtime.storage.listReminders(filterAuthorId);
        const selectedUser = filterAuthorId
          ? interaction.data?.resolved?.users?.[filterAuthorId]
          : undefined;
        const title = selectedUser
          ? `Reminders for ${selectedUser.global_name ?? selectedUser.username}`
          : undefined;
        const stateId = crypto.randomUUID();
        const now = Date.now();
        await runtime.storage.createInteractionState({
          id: stateId,
          kind: "reminders_page",
          ownerUserId: authorId,
          guildId: interaction.guild_id!,
          channelId: interaction.channel_id!,
          payload: {
            ...(filterAuthorId ? { filterAuthorId } : {}),
            ...(title ? { title } : {}),
          },
          createdAt: now,
          expiresAt: now + PAGE_TTL_MS,
        });
        await finish(
          interaction,
          runtime,
          renderReminderPage(reminders, 0, stateId, title),
        );
      });
    }

    const reminderId = integerOption(interaction, "reminder_id");
    return deferredTask(interaction, runtime, true, async () => {
      const reminder = await runtime.storage.getReminder(reminderId);
      if (!reminder) {
        await finish(
          interaction,
          runtime,
          `Reminder with ID ${reminderId} not found.`,
        );
        return;
      }
      if (reminder.authorId !== authorId && !hasAdministrator(interaction)) {
        await finish(
          interaction,
          runtime,
          "You can only delete your own reminders.",
        );
        return;
      }
      await runtime.storage.deleteReminder(reminderId);
      await runtime.scheduler.reconcile().catch((error) =>
        logError("reminder_reconcile_failed", error, {
          interaction_id: interaction.id,
          reminder_id: reminderId,
        }),
      );
      await finish(
        interaction,
        runtime,
        `Reminder ${reminderId} has been deleted successfully!`,
      );
    });
  },
};
