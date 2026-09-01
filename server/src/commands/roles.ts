import {
  ApplicationCommandOptionType,
  ApplicationCommandType,
} from "discord-api-types/v10";
import {
  addGuildMemberRole,
  removeGuildMemberRole,
} from "../discord/client.js";
import { autocomplete, message } from "../discord/responses.js";
import { deferredTask, finish, hasAnyRole } from "./helpers.js";
import {
  focusedOption,
  guildId,
  stringOption,
  subcommand,
  userId,
} from "./options.js";
import type { CommandDefinition } from "./types.js";

export const rolesCommand: CommandDefinition = {
  command: {
    name: "roles",
    type: ApplicationCommandType.ChatInput,
    description: "No Description Set",
    options: [
      {
        type: ApplicationCommandOptionType.Subcommand,
        name: "add",
        description: "Add yourself to a team role. Requires the UIUC role.",
        options: [
          {
            type: ApplicationCommandOptionType.String,
            name: "role",
            description: "Role to add",
            required: true,
            autocomplete: true,
          },
        ],
      },
      {
        type: ApplicationCommandOptionType.Subcommand,
        name: "remove",
        description: "Remove yourself from a team role.",
        options: [
          {
            type: ApplicationCommandOptionType.String,
            name: "role",
            description: "Role to remove",
            required: true,
            autocomplete: true,
          },
        ],
      },
    ],
  },
  async handle(interaction, runtime) {
    const targetGuildId = guildId(interaction);
    if (!targetGuildId) {
      return message(":x: You can only run this command in a server.", true);
    }

    const action = subcommand(interaction)?.name;
    const roleName = stringOption(interaction, "role");
    const memberRoles = interaction.member?.roles ?? [];
    if (action === "add") {
      if (!hasAnyRole(interaction, runtime.env.UIUC_ROLES)) {
        return message(
          ":x: You need to be UIUC verified to use this command. Verify yourself at <https://sigpwny.com/auth>.",
          true,
        );
      }
    }

    const configuredRole = runtime.env.PRIVATE_ROLES.find(
      (role) => role.name.toLowerCase() === roleName.toLowerCase(),
    );
    if (!configuredRole) {
      return message(":x: Invalid role.");
    }

    if (action === "add") {
      if (memberRoles.includes(configuredRole.discordRoleId)) {
        return message(
          `:x: You already have the **${configuredRole.name}** role.`,
          true,
        );
      }
      return deferredTask(interaction, runtime, false, async () => {
        await addGuildMemberRole(
          runtime.env,
          targetGuildId,
          userId(interaction),
          configuredRole.discordRoleId,
        );
        await finish(
          interaction,
          runtime,
          `:white_check_mark: Added to **${configuredRole.name}**.`,
        );
      });
    }

    if (!memberRoles.includes(configuredRole.discordRoleId)) {
      return message(
        `:x: You do not have the **${configuredRole.name}** role.`,
        true,
      );
    }
    return deferredTask(interaction, runtime, false, async () => {
      await removeGuildMemberRole(
        runtime.env,
        targetGuildId,
        userId(interaction),
        configuredRole.discordRoleId,
      );
      await finish(
        interaction,
        runtime,
        `:white_check_mark: Removed from **${configuredRole.name}**.`,
      );
    });
  },
  async autocomplete(interaction, runtime) {
    const current = String(focusedOption(interaction)?.value ?? "");
    return autocomplete(
      runtime.env.PRIVATE_ROLES.filter((role) =>
        role.name.toLowerCase().includes(current.toLowerCase()),
      ).map((role) => ({ name: role.name, value: role.name })),
    );
  },
};
