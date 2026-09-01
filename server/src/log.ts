import { discordErrorMetadata } from "./discord/client.js";
import type { DiscordInteraction } from "./discord/types.js";

export function logError(
  event: string,
  error: unknown,
  metadata: Record<string, string | number | boolean | undefined> = {},
): void {
  const discordError = discordErrorMetadata(error);
  console.error(
    JSON.stringify({
      level: "error",
      event,
      error_type: error instanceof Error ? error.name : "unknown",
      discord_status: discordError.status,
      discord_route: discordError.route,
      ...metadata,
    }),
  );
}

export function logInteractionError(
  event: string,
  interaction: DiscordInteraction,
  error: unknown,
): void {
  logError(event, error, {
    interaction_id: interaction.id,
    command: interaction.data?.name,
    guild_id: interaction.guild_id,
    channel_id: interaction.channel_id,
    user_id: interaction.member?.user?.id ?? interaction.user?.id,
  });
}
