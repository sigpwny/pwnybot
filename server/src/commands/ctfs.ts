import {
  addGuildMemberRole,
  removeGuildMemberRole,
} from "../discord/client.js";
import { message } from "../discord/responses.js";
import { deferredTask, finish, hasAnyRole } from "./helpers.js";
import { guildId, userId, subcommand } from "./options.js";
import type { CommandDefinition } from "./types.js";

export const ctfsCommand: CommandDefinition = {
  command: {
    name: "ctfs",
    type: 1,
    description: "No Description Set",
    contexts: [0],
    integration_types: [0],
    options: [
      {
        type: 1,
        name: "optin",
        description: "Add yourself to the CTF Team. Requires the UIUC role.",
      },
      {
        type: 1,
        name: "optout",
        description: "Remove yourself from the CTF Team.",
      },
    ],
  },
  async handle(interaction, runtime) {
    const targetGuildId = guildId(interaction);
    if (!targetGuildId) {
      return message(":x: You can only run this command in a server.", true);
    }

    const action = subcommand(interaction)?.name;
    const memberRoles = new Set(interaction.member?.roles ?? []);
    const assignedCtfRoles = runtime.env.CTF_ROLES.filter((roleId) =>
      memberRoles.has(roleId),
    );
    if (action === "optin") {
      if (!hasAnyRole(interaction, runtime.env.UIUC_ROLES)) {
        return message(
          ":x: You need to be UIUC verified to use this command. Verify yourself at <https://sigpwny.com/auth>.",
          true,
        );
      }
      const missingRoles = runtime.env.CTF_ROLES.filter(
        (roleId) => !memberRoles.has(roleId),
      );
      if (missingRoles.length === 0) {
        return message(
          ":x: You already have the **:red_circle: CTF Team** role.",
          true,
        );
      }
      return deferredTask(interaction, runtime, false, async () => {
        for (const roleId of missingRoles) {
          await addGuildMemberRole(
            runtime.env,
            targetGuildId,
            userId(interaction),
            roleId,
          );
        }
        await finish(
          interaction,
          runtime,
          ":white_check_mark: Added to **:red_circle: CTF Team**.",
        );
      });
    }

    if (assignedCtfRoles.length === 0) {
      return message(
        ":x: You do not have the **:red_circle: CTF Team** role.",
        true,
      );
    }
    return deferredTask(interaction, runtime, false, async () => {
      for (const roleId of runtime.env.CTF_ROLES) {
        await removeGuildMemberRole(
          runtime.env,
          targetGuildId,
          userId(interaction),
          roleId,
        );
      }
      await finish(
        interaction,
        runtime,
        ":white_check_mark: Removed from **:red_circle: CTF Team**.",
      );
    });
  },
};
