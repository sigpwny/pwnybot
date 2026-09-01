import type { DiscordInteraction } from "../discord/types.js";
import { dispatchComponent, dispatchModal } from "./components.js";
import { basicCommands } from "./basic.js";
import { chalCommand } from "./chal.js";
import { copypastaCommand } from "./copypasta.js";
import { ctfCommand } from "./ctf.js";
import { ctfsCommand } from "./ctfs.js";
import { managerCommand } from "./manager.js";
import { remindersCommand } from "./reminders.js";
import { rolesCommand } from "./roles.js";
import type { CommandDefinition, CommandRuntime } from "./types.js";

export const commandDefinitions: CommandDefinition[] = [
  ...basicCommands,
  chalCommand,
  ctfCommand,
  ctfsCommand,
  rolesCommand,
  managerCommand,
  copypastaCommand,
  remindersCommand,
];

export const commandPayloads = commandDefinitions.map(
  (definition) => definition.command,
);

export async function dispatchCommand(
  interaction: DiscordInteraction,
  runtime: CommandRuntime,
): Promise<Response> {
  if (interaction.type === 3) {
    return dispatchComponent(interaction, runtime);
  }
  if (interaction.type === 5) {
    return dispatchModal(interaction, runtime);
  }
  const definition = commandDefinitions.find(
    (candidate) => candidate.command.name === interaction.data?.name,
  );
  if (!definition) {
    return new Response(
      JSON.stringify({
        type: 4,
        data: { content: ":x: Unknown command.", flags: 64 },
      }),
      {
        headers: { "Content-Type": "application/json" },
      },
    );
  }
  return interaction.type === 4 && definition.autocomplete
    ? definition.autocomplete(interaction, runtime)
    : definition.handle(interaction, runtime);
}
