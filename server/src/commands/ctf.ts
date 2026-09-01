import {
  ApplicationCommandOptionType,
  ApplicationCommandType,
  ChannelType,
  OverwriteType,
  PermissionFlagsBits,
} from "discord-api-types/v10";
import {
  createForumPost,
  createGuildChannel,
  editChannel,
  getCurrentUser,
  listGuildChannels,
  listGuildRoles,
  pinForumPost,
  addChannelPermission,
} from "../discord/client.js";
import { message } from "../discord/responses.js";
import type { DiscordForumTag } from "../discord/types.js";
import { logError } from "../log.js";
import { deferredTask, finish } from "./helpers.js";
import { getCtfContext } from "./ctf-context.js";
import { guildId, option, stringOption, subcommand } from "./options.js";
import type { CommandDefinition } from "./types.js";

const VIEW_CHANNEL = String(PermissionFlagsBits.ViewChannel);
const GENERAL = "General";
const CHALLENGE_CATEGORIES = [
  "crypto",
  "forensics",
  "misc",
  "pwn",
  "osint",
  "rev",
  "web",
];

export function sanitizeName(name: string, maxLength = 32): string {
  return name
    .toLowerCase()
    .replaceAll(" ", "-")
    .replace(/[^a-z0-9_-]/g, "")
    .replace(/--+/g, "-")
    .slice(0, maxLength);
}

function newTag(name: string): Omit<DiscordForumTag, "id"> {
  return { name, moderated: false, emoji_id: null, emoji_name: null };
}

export const ctfCommand: CommandDefinition = {
  command: {
    name: "ctf",
    type: ApplicationCommandType.ChatInput,
    description: "No Description Set",
    default_member_permissions: String(PermissionFlagsBits.Administrator),
    options: [
      {
        type: ApplicationCommandOptionType.Subcommand,
        name: "create",
        description: "Creates a forum for the CTF",
        options: [
          {
            type: ApplicationCommandOptionType.String,
            name: "name",
            description: "The name of the CTF",
            required: true,
          },
        ],
      },
      {
        type: ApplicationCommandOptionType.Subcommand,
        name: "addcategory",
        description: "Adds tags for a custom category",
        options: [
          {
            type: ApplicationCommandOptionType.String,
            name: "category",
            description: "The name of the category",
            required: true,
          },
        ],
      },
      {
        type: ApplicationCommandOptionType.Subcommand,
        name: "addrole",
        description: "Adds a user or role to a CTF",
        options: [
          {
            type: ApplicationCommandOptionType.Mentionable,
            name: "target",
            description: "The user or role to add to this CTF",
            required: true,
          },
        ],
      },
    ],
  },
  async handle(interaction, runtime) {
    const targetGuildId = guildId(interaction);
    if (!targetGuildId) {
      return message(":x: Must be used inside a guild.");
    }

    const action = subcommand(interaction)?.name;
    if (action === "create") {
      return deferredTask(interaction, runtime, false, async () => {
        const [channels, roles, botUser] = await Promise.all([
          listGuildChannels(runtime.env, targetGuildId),
          listGuildRoles(runtime.env, targetGuildId),
          getCurrentUser(runtime.env),
        ]);
        let parentId: string | undefined;
        for (const configuredId of runtime.env.CTF_CATEGORY_CHANNELS) {
          if (channels.some((channel) => channel.id === configuredId)) {
            parentId = configuredId;
          }
        }

        const tagNames = CHALLENGE_CATEGORIES.flatMap((category) => [
          category,
          `unsolved-${category}`,
        ]);
        tagNames.push("unsolved");
        const permissionOverwrites = [
          {
            id: botUser.id,
            type: OverwriteType.Member,
            allow: VIEW_CHANNEL,
            deny: "0",
          },
          {
            id: targetGuildId,
            type: OverwriteType.Role,
            allow: "0",
            deny: VIEW_CHANNEL,
          },
          ...runtime.env.CTF_ROLES.filter((roleId) =>
            roles.some((role) => role.id === roleId),
          ).map((roleId) => ({
            id: roleId,
            type: OverwriteType.Role,
            allow: VIEW_CHANNEL,
            deny: "0",
          })),
        ];
        const forum = await createGuildChannel(runtime.env, targetGuildId, {
          name: sanitizeName(`ctf-${stringOption(interaction, "name")}`, 100),
          type: ChannelType.GuildForum,
          position: 1000,
          parent_id: parentId,
          available_tags: tagNames.map(newTag),
          permission_overwrites: permissionOverwrites,
        });

        try {
          const general = await createForumPost(
            runtime.env,
            forum.id,
            GENERAL,
            "To get started, run `/chal create <name> <category>`\nSolve a challenge in its respective channel with `/chal solve <flag>`",
          );
          await pinForumPost(runtime.env, general);
          await finish(interaction, runtime, `Created <#${forum.id}>.`);
        } catch (error) {
          logError("ctf_initialization_partial", error, {
            guild_id: targetGuildId,
            forum_id: forum.id,
          });
          await finish(
            interaction,
            runtime,
            `:x: Created <#${forum.id}>, but initialization failed. Repair the forum manually.`,
          );
        }
      });
    }

    return deferredTask(interaction, runtime, false, async () => {
      const context = await getCtfContext(runtime.env, interaction, true);
      if (!context || context.post.name !== GENERAL) {
        await finish(
          interaction,
          runtime,
          ":x: Must be used inside a CTF forum's general channel.",
        );
        return;
      }

      if (action === "addcategory") {
        const category = stringOption(interaction, "category");
        if (category.toLowerCase().includes("unsolved")) {
          await finish(
            interaction,
            runtime,
            ":x: Unsolved cannot be a category.",
          );
          return;
        }
        const tags = context.forum.available_tags ?? [];
        if (
          tags.some((tag) => tag.name.toLowerCase() === category.toLowerCase())
        ) {
          await finish(
            interaction,
            runtime,
            `:x: Category ${category} already exists.`,
          );
          return;
        }
        const first = await editChannel(runtime.env, context.forum.id, {
          available_tags: [...tags, newTag(category)],
        });
        await editChannel(runtime.env, context.forum.id, {
          available_tags: [
            ...(first.available_tags ?? []),
            newTag(`unsolved-${category}`),
          ],
        });
        await finish(interaction, runtime, `Added tags for ${category}.`);
        return;
      }

      const target = String(option(interaction, "target")?.value ?? "");
      const targetType = interaction.data?.resolved?.roles?.[target]
        ? OverwriteType.Role
        : OverwriteType.Member;
      await addChannelPermission(
        runtime.env,
        context.forum,
        target,
        targetType,
        BigInt(VIEW_CHANNEL),
      );
      await finish(
        interaction,
        runtime,
        `Added <@${targetType === 0 ? "&" : ""}${target}> to the CTF`,
      );
    });
  },
};
