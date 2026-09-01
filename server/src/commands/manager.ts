import {
  ApplicationCommandOptionType,
  ApplicationCommandType,
  ButtonStyle,
  ChannelType,
  ComponentType,
  PermissionFlagsBits,
} from "discord-api-types/v10";
import {
  addGuildMemberRole,
  editOriginalInteractionResponseWithFile,
  listChannelMessages,
  listGuildRoles,
  searchGuildMembers,
} from "../discord/client.js";
import { message, modal } from "../discord/responses.js";
import { deferredTask, finish } from "./helpers.js";
import {
  channelId,
  guildId,
  stringOption,
  subcommand,
  userId,
} from "./options.js";
import type { CommandDefinition } from "./types.js";

const ACTION_TTL_MS = 60_000;
const MODAL_TTL_MS = 15 * 60_000;

export const managerCommand: CommandDefinition = {
  command: {
    name: "manager",
    type: ApplicationCommandType.ChatInput,
    description: "No Description Set",
    default_member_permissions: String(PermissionFlagsBits.Administrator),
    options: [
      {
        type: ApplicationCommandOptionType.Subcommand,
        name: "say",
        description: "Says your previous message in the channel you specify",
        options: [
          {
            type: ApplicationCommandOptionType.Channel,
            name: "channel",
            description: "The channel to send the message in",
            required: true,
            channel_types: [ChannelType.GuildText],
          },
        ],
      },
      {
        type: ApplicationCommandOptionType.Subcommand,
        name: "edit",
        description: "Edits a message said by the bot",
        options: [
          {
            type: ApplicationCommandOptionType.Channel,
            name: "message_channel",
            description: "The channel of the original message",
            required: true,
            channel_types: [ChannelType.GuildText],
          },
          {
            type: ApplicationCommandOptionType.String,
            name: "message_id",
            description: "The ID of the message to edit",
            required: true,
          },
        ],
      },
      {
        type: ApplicationCommandOptionType.Subcommand,
        name: "assign_roles",
        description: "Assigns a role to a list of users by username.",
        options: [
          {
            type: ApplicationCommandOptionType.String,
            name: "role_name",
            description: "The name of the role to assign",
            required: true,
          },
          {
            type: ApplicationCommandOptionType.String,
            name: "usernames",
            description:
              'A comma-separated list of usernames (e.g. "user1, user2")',
            required: true,
          },
        ],
      },
    ],
  },
  async handle(interaction, runtime) {
    const targetGuildId = guildId(interaction);
    const invocationChannelId = channelId(interaction);
    if (!targetGuildId || !invocationChannelId) {
      return message(":x: Could not determine the guild context.");
    }

    const action = subcommand(interaction)?.name;
    if (action === "say") {
      return deferredTask(interaction, runtime, true, async () => {
        const authorId = userId(interaction);
        const source = (
          await listChannelMessages(runtime.env, invocationChannelId)
        ).find((candidate) => candidate.author.id === authorId);
        if (!source?.content) {
          await finish(
            interaction,
            runtime,
            ":x: Send the message in the current channel before calling /manager say.",
          );
          return;
        }

        const id = crypto.randomUUID();
        const now = Date.now();
        const targetChannelId = stringOption(interaction, "channel");
        await runtime.storage.createInteractionState({
          id,
          kind: "manager_say",
          ownerUserId: authorId,
          guildId: targetGuildId,
          channelId: invocationChannelId,
          payload: { targetChannelId, content: source.content },
          createdAt: now,
          expiresAt: now + ACTION_TTL_MS,
        });
        await finish(interaction, runtime, {
          content: `Should I send this in <#${targetChannelId}>? (60s expiry)`,
          embeds: [{ description: source.content }],
          components: [
            {
              type: ComponentType.ActionRow,
              components: [
                {
                  type: ComponentType.Button,
                  style: ButtonStyle.Success,
                  label: "Confirm",
                  custom_id: `manager-say:confirm:${id}`,
                },
                {
                  type: ComponentType.Button,
                  style: ButtonStyle.Secondary,
                  label: "Cancel",
                  custom_id: `manager-say:cancel:${id}`,
                },
              ],
            },
          ],
        });
      });
    }

    if (action === "edit") {
      const id = interaction.id;
      const now = Date.now();
      await runtime.storage.createInteractionState({
        id,
        kind: "manager_edit",
        ownerUserId: userId(interaction),
        guildId: targetGuildId,
        channelId: invocationChannelId,
        payload: {
          targetChannelId: stringOption(interaction, "message_channel"),
          targetMessageId: stringOption(interaction, "message_id"),
        },
        createdAt: now,
        expiresAt: now + MODAL_TTL_MS,
      });
      return modal(
        `manager-edit:${id}`,
        "Edit bot message",
        "Replacement message",
      );
    }

    const roleName = stringOption(interaction, "role_name");
    const usernames = stringOption(interaction, "usernames")
      .replaceAll(", ", ",")
      .split(",")
      .map((username) => username.trim())
      .filter(Boolean);
    if (usernames.length === 0) {
      return message(":x: Please provide a comma-separated list of usernames.");
    }

    return deferredTask(interaction, runtime, false, async () => {
      const role = (await listGuildRoles(runtime.env, targetGuildId)).find(
        (candidate) => candidate.name.toLowerCase() === roleName.toLowerCase(),
      );
      if (!role) {
        await finish(interaction, runtime, `:x: Role '${roleName}' not found.`);
        return;
      }

      const assigned: string[] = [];
      const notFound: string[] = [];
      for (const username of usernames) {
        const candidates = await searchGuildMembers(
          runtime.env,
          targetGuildId,
          username,
        );
        const member = candidates.find(
          (candidate) =>
            candidate.user?.username.toLowerCase() === username.toLowerCase(),
        );
        if (!member?.user) {
          notFound.push(username);
          continue;
        }
        try {
          await addGuildMemberRole(
            runtime.env,
            targetGuildId,
            member.user.id,
            role.id,
          );
          assigned.push(username);
        } catch {
          notFound.push(username);
        }
      }

      const details = [
        assigned.length
          ? `Assigned role '${role.name}' to: ${assigned.join(", ")}`
          : "No roles assigned.",
        notFound.length
          ? `Could not find or assign role to: ${notFound.join(", ")}`
          : "No assignment failures.",
      ].join("\n");
      const summary = `:white_check_mark: Assigned: ${assigned.length}\n:x: Not assigned: ${notFound.length}`;
      if (details.length > 1_900) {
        await editOriginalInteractionResponseWithFile(
          runtime.env,
          interaction.token,
          { content: summary },
          "role-assignment-report.txt",
          details,
        );
      } else {
        await finish(interaction, runtime, `${summary}\n${details}`);
      }
    });
  },
};
