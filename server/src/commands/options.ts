import { ApplicationCommandOptionType } from "discord-api-types/v10";
import type {
  DiscordCommandOption,
  DiscordInteraction,
} from "../discord/types.js";

export function subcommand(
  interaction: DiscordInteraction,
): DiscordCommandOption | undefined {
  return interaction.data?.options?.find(
    (option) => option.type === ApplicationCommandOptionType.Subcommand,
  );
}

export function options(
  interaction: DiscordInteraction,
): DiscordCommandOption[] {
  return subcommand(interaction)?.options ?? interaction.data?.options ?? [];
}

export function option(
  interaction: DiscordInteraction,
  name: string,
): DiscordCommandOption | undefined {
  return options(interaction).find((candidate) => candidate.name === name);
}

export function stringOption(
  interaction: DiscordInteraction,
  name: string,
  fallback?: string,
): string {
  const value = option(interaction, name)?.value;
  if (typeof value === "string") {
    return value;
  }
  if (fallback !== undefined) {
    return fallback;
  }
  throw new Error(`Missing string option: ${name}`);
}

export function integerOption(
  interaction: DiscordInteraction,
  name: string,
  fallback?: number,
): number {
  const value = option(interaction, name)?.value;
  if (typeof value === "number" && Number.isInteger(value)) {
    return value;
  }
  if (fallback !== undefined) {
    return fallback;
  }
  throw new Error(`Missing integer option: ${name}`);
}

export function booleanOption(
  interaction: DiscordInteraction,
  name: string,
  fallback = false,
): boolean {
  const value = option(interaction, name)?.value;
  return typeof value === "boolean" ? value : fallback;
}

export function focusedOption(
  interaction: DiscordInteraction,
): DiscordCommandOption | undefined {
  return options(interaction).find((candidate) => candidate.focused);
}

export function userId(interaction: DiscordInteraction): string {
  const id = interaction.member?.user?.id ?? interaction.user?.id;
  if (!id) {
    throw new Error("Interaction has no user");
  }
  return id;
}

export function guildId(interaction: DiscordInteraction): string | null {
  return interaction.guild_id ?? null;
}

export function channelId(interaction: DiscordInteraction): string | null {
  return interaction.channel_id ?? null;
}
