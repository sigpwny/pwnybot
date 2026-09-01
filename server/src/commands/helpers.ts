import { editOriginalInteractionResponse } from "../discord/client.js";
import { deferred, deferredUpdate, message } from "../discord/responses.js";
import type {
  DiscordInteraction,
  InteractionMessageData,
} from "../discord/types.js";
import { logInteractionError } from "../log.js";
import type { CommandRuntime } from "./types.js";

export function hasAnyRole(
  interaction: DiscordInteraction,
  roleIds: string[],
): boolean {
  return (
    interaction.member?.roles.some((roleId) => roleIds.includes(roleId)) ??
    false
  );
}

export function hasAdministrator(interaction: DiscordInteraction): boolean {
  const permissions = interaction.member?.permissions;
  return permissions ? (BigInt(permissions) & 8n) !== 0n : false;
}

export async function afterInteractionAck(): Promise<void> {
  await new Promise<void>((resolve) => setTimeout(resolve, 50));
}

export async function claimInteraction(
  interaction: DiscordInteraction,
  runtime: CommandRuntime,
): Promise<boolean> {
  return runtime.storage.claimInteraction(
    interaction.id,
    Date.now() + 24 * 60 * 60_000,
  );
}

async function runClaimedTask(
  interaction: DiscordInteraction,
  runtime: CommandRuntime,
  task: () => Promise<void>,
): Promise<void> {
  await afterInteractionAck();
  if (!(await claimInteraction(interaction, runtime))) {
    return;
  }
  await task();
}

export function deferredTask(
  interaction: DiscordInteraction,
  runtime: CommandRuntime,
  ephemeral: boolean,
  task: () => Promise<void>,
): Response {
  runtime.background.waitUntil(
    runClaimedTask(interaction, runtime, task).catch(async (error) => {
      logInteractionError("deferred_command_failed", interaction, error);
      await editOriginalInteractionResponse(runtime.env, interaction.token, {
        content: ":x: An error has occured.",
      }).catch((followupError) =>
        logInteractionError(
          "command_error_response_failed",
          interaction,
          followupError,
        ),
      );
    }),
  );
  return deferred(ephemeral);
}

export function deferredUpdateTask(
  interaction: DiscordInteraction,
  runtime: CommandRuntime,
  task: () => Promise<void>,
): Response {
  runtime.background.waitUntil(
    runClaimedTask(interaction, runtime, task).catch(async (error) => {
      logInteractionError("component_task_failed", interaction, error);
      await editOriginalInteractionResponse(runtime.env, interaction.token, {
        content: ":x: This action failed.",
        components: [],
      }).catch((responseError) =>
        logInteractionError(
          "component_error_response_failed",
          interaction,
          responseError,
        ),
      );
    }),
  );
  return deferredUpdate();
}

export async function finish(
  interaction: DiscordInteraction,
  runtime: CommandRuntime,
  data: string | InteractionMessageData,
): Promise<void> {
  await editOriginalInteractionResponse(
    runtime.env,
    interaction.token,
    typeof data === "string" ? { content: data } : data,
  );
}

export function requireGuild(
  interaction: DiscordInteraction,
): { guildId: string; channelId: string } | Response {
  if (!interaction.guild_id || !interaction.channel_id) {
    return message(":x: Must be used inside a guild.");
  }
  return { guildId: interaction.guild_id, channelId: interaction.channel_id };
}
