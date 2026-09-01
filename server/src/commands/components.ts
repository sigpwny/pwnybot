import {
  createChannelMessage,
  editChannelMessage,
  getChannelMessage,
  getCurrentUser,
} from "../discord/client.js";
import { message, updateMessage } from "../discord/responses.js";
import type { DiscordComponent, DiscordInteraction } from "../discord/types.js";
import { deferredTask, deferredUpdateTask, finish } from "./helpers.js";
import { renderReminderPage } from "./reminders.js";
import { userId } from "./options.js";
import type { CommandRuntime } from "./types.js";

function lookup(interaction: DiscordInteraction, id: string, kind: string) {
  if (!interaction.guild_id || !interaction.channel_id) {
    return null;
  }
  return {
    id,
    kind,
    ownerUserId: userId(interaction),
    guildId: interaction.guild_id,
    channelId: interaction.channel_id,
    now: Date.now(),
  };
}

function textInput(components: DiscordComponent[] | undefined): string | null {
  for (const component of components ?? []) {
    if (
      component.custom_id === "content" &&
      typeof component.value === "string"
    ) {
      return component.value;
    }
    const nested = textInput(component.components);
    if (nested !== null) {
      return nested;
    }
  }
  return null;
}

export async function dispatchComponent(
  interaction: DiscordInteraction,
  runtime: CommandRuntime,
): Promise<Response> {
  const customId = interaction.data?.custom_id ?? "";
  const [prefix, action, id] = customId.split(":");

  if (prefix === "manager-say" && id) {
    const stateLookup = lookup(interaction, id, "manager_say");
    if (!stateLookup) {
      return message("This confirmation is no longer valid.", true);
    }
    if (!(await runtime.storage.getInteractionState(stateLookup))) {
      return message(
        "This confirmation expired or belongs to another user.",
        true,
      );
    }
    return deferredUpdateTask(interaction, runtime, async () => {
      const state = await runtime.storage.consumeInteractionState(stateLookup);
      if (!state) {
        await finish(interaction, runtime, {
          content: "This confirmation expired or was already used.",
          components: [],
          embeds: interaction.message?.embeds,
        });
        return;
      }
      if (action === "confirm") {
        await createChannelMessage(
          runtime.env,
          String(state.payload.targetChannelId),
          String(state.payload.content),
        );
        await finish(interaction, runtime, {
          content: `:white_check_mark: Sent message in <#${String(state.payload.targetChannelId)}>.`,
          components: [],
          embeds: interaction.message?.embeds,
        });
      } else {
        await finish(interaction, runtime, {
          content: "Cancelled.",
          components: [],
          embeds: interaction.message?.embeds,
        });
      }
    });
  }

  if (prefix === "reminders-page" && action && id) {
    const stateLookup = lookup(interaction, action, "reminders_page");
    if (!stateLookup) {
      return message("This reminder list is no longer valid.", true);
    }
    if (!(await runtime.storage.getInteractionState(stateLookup))) {
      return message(
        "This reminder list expired or belongs to another user.",
        true,
      );
    }
    const requestedPage = Number(id);
    return deferredUpdateTask(interaction, runtime, async () => {
      const state = await runtime.storage.getInteractionState(stateLookup);
      if (!state || !Number.isInteger(requestedPage)) {
        await finish(interaction, runtime, {
          content: "This reminder list expired.",
          embeds: [],
          components: [],
        });
        return;
      }
      const filterAuthorId =
        typeof state.payload.filterAuthorId === "string"
          ? state.payload.filterAuthorId
          : undefined;
      const reminders = await runtime.storage.listReminders(filterAuthorId);
      await finish(
        interaction,
        runtime,
        renderReminderPage(
          reminders,
          requestedPage,
          state.id,
          typeof state.payload.title === "string"
            ? state.payload.title
            : undefined,
        ),
      );
    });
  }

  return updateMessage({
    content: "Unknown or expired action.",
    components: [],
  });
}

export async function dispatchModal(
  interaction: DiscordInteraction,
  runtime: CommandRuntime,
): Promise<Response> {
  const customId = interaction.data?.custom_id ?? "";
  const [prefix, id] = customId.split(":");
  if (prefix !== "manager-edit" || !id) {
    return message("Unknown modal submission.", true);
  }
  const stateLookup = lookup(interaction, id, "manager_edit");
  const content = textInput(interaction.data?.components);
  if (!stateLookup || !content) {
    return message("This edit request is invalid or expired.", true);
  }
  if (!(await runtime.storage.getInteractionState(stateLookup))) {
    return message(
      "This edit request expired or belongs to another user.",
      true,
    );
  }

  return deferredTask(interaction, runtime, true, async () => {
    const state = await runtime.storage.consumeInteractionState(stateLookup);
    if (!state) {
      await finish(
        interaction,
        runtime,
        "This edit request expired or was already used.",
      );
      return;
    }
    const targetChannelId = String(state.payload.targetChannelId);
    const targetMessageId = String(state.payload.targetMessageId);
    const [target, bot] = await Promise.all([
      getChannelMessage(runtime.env, targetChannelId, targetMessageId),
      getCurrentUser(runtime.env),
    ]);
    if (!target) {
      await finish(interaction, runtime, ":x: Unable to find message");
      return;
    }
    if (target.author.id !== bot.id) {
      await finish(interaction, runtime, ":x: Message must be from the bot");
      return;
    }
    await editChannelMessage(
      runtime.env,
      targetChannelId,
      targetMessageId,
      content,
    );
    await finish(interaction, runtime, ":white_check_mark: edited message.");
  });
}
