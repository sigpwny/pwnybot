import {
  ApplicationCommandOptionType,
  ApplicationCommandType,
} from "discord-api-types/v10";
import {
  createChannelMessage,
  createForumPost,
  editChannel,
  listForumPosts,
} from "../discord/client.js";
import { autocomplete } from "../discord/responses.js";
import { getCtfContext } from "./ctf-context.js";
import { deferredTask, finish } from "./helpers.js";
import { focusedOption, stringOption, subcommand, userId } from "./options.js";
import type { CommandDefinition } from "./types.js";

const GENERAL = "General";

export const chalCommand: CommandDefinition = {
  command: {
    name: "chal",
    type: ApplicationCommandType.ChatInput,
    description: "No Description Set",
    options: [
      {
        type: ApplicationCommandOptionType.Subcommand,
        name: "create",
        description: "Creates a channel for the challenge",
        options: [
          {
            type: ApplicationCommandOptionType.String,
            name: "name",
            description: "The name of the challenge",
            required: true,
          },
          {
            type: ApplicationCommandOptionType.String,
            name: "category",
            description: "the category of the challenge",
            required: true,
            autocomplete: true,
          },
        ],
      },
      {
        type: ApplicationCommandOptionType.Subcommand,
        name: "solve",
        description: "Marks a challenge as solved with a flag",
        options: [
          {
            type: ApplicationCommandOptionType.String,
            name: "flag",
            description: "The flag for the challenge",
            required: true,
          },
        ],
      },
    ],
  },
  async handle(interaction, runtime) {
    const action = subcommand(interaction)?.name;
    return deferredTask(interaction, runtime, false, async () => {
      const context = await getCtfContext(runtime.env, interaction, true);
      if (!context) {
        await finish(
          interaction,
          runtime,
          ":x: Must be used inside a CTF forum.",
        );
        return;
      }

      if (action === "create") {
        if (context.post.name !== GENERAL) {
          await finish(
            interaction,
            runtime,
            ":x: Must be used inside a CTF forum's general channel.",
          );
          return;
        }
        const category = stringOption(interaction, "category");
        if (category.toLowerCase().includes("unsolved")) {
          await finish(
            interaction,
            runtime,
            ":x: Unsolved cannot be a category.",
          );
          return;
        }
        const name = stringOption(interaction, "name");
        const posts = await listForumPosts(
          runtime.env,
          interaction.guild_id!,
          context.forum.id,
        );
        const duplicate = posts.find((post) => {
          const postName = post.name?.startsWith("✔-")
            ? post.name.slice(2)
            : post.name;
          return postName?.toLowerCase() === name.toLowerCase();
        });
        if (duplicate) {
          await finish(
            interaction,
            runtime,
            `:x: Challenge <#${duplicate.id}> already exists.`,
          );
          return;
        }
        const tags = context.forum.available_tags ?? [];
        const categoryTag = tags.find(
          (tag) => tag.name.toLowerCase() === category.toLowerCase(),
        );
        if (!categoryTag) {
          await finish(
            interaction,
            runtime,
            `:x: Could not find category ${category}.`,
          );
          return;
        }
        const unsolved = tags.find((tag) => tag.name === "unsolved");
        const unsolvedCategory = tags.find(
          (tag) =>
            tag.name.toLowerCase() ===
            `unsolved-${categoryTag?.name ?? category}`.toLowerCase(),
        );
        const post = await createForumPost(
          runtime.env,
          context.forum.id,
          name,
          name,
          [categoryTag, unsolved, unsolvedCategory]
            .filter((tag) => Boolean(tag))
            .map((tag) => tag!.id),
        );
        await finish(
          interaction,
          runtime,
          `<@${userId(interaction)}> created <#${post.id}>.`,
        );
        return;
      }

      if (context.post.name === GENERAL) {
        await finish(
          interaction,
          runtime,
          ":x: Cannot be used inside a CTF forum's general channel.",
        );
        return;
      }
      const tags = context.forum.available_tags ?? [];
      const appliedTags = (context.post.applied_tags ?? [])
        .map((id) => tags.find((tag) => tag.id === id))
        .filter(Boolean);
      if (!appliedTags.some((tag) => tag!.name.includes("unsolved"))) {
        await finish(
          interaction,
          runtime,
          `:x: Challenge does not have unsolved tag. Has tags: ${appliedTags.map((tag) => tag!.name).join(", ")}`,
        );
        return;
      }

      const remainingTagIds = appliedTags
        .filter((tag) => !tag!.name.includes("unsolved"))
        .map((tag) => tag!.id);
      await finish(interaction, runtime, "Marking challenge as solved.");
      await editChannel(runtime.env, context.post.id, {
        name: `✔-${context.post.name ?? ""}`,
        applied_tags: remainingTagIds,
        archived: true,
      });
      const posts = await listForumPosts(
        runtime.env,
        interaction.guild_id!,
        context.forum.id,
      );
      const general = posts.find((post) => post.name === GENERAL);
      if (general) {
        await createChannelMessage(
          runtime.env,
          general.id,
          `<@${userId(interaction)}> solved challenge <#${context.post.id}> with ||${stringOption(interaction, "flag")}||`,
        );
      }
    });
  },
  async autocomplete(interaction, runtime) {
    const context = await getCtfContext(runtime.env, interaction);
    if (!context || context.post.name !== GENERAL) {
      return autocomplete([
        {
          name: "Must be used inside a CTF forum's general channel.",
          value: "Must be used inside a CTF forum's general channel.",
        },
      ]);
    }
    const current = String(focusedOption(interaction)?.value ?? "");
    return autocomplete(
      (context.forum.available_tags ?? [])
        .filter(
          (tag) =>
            tag.name.toLowerCase().includes(current.toLowerCase()) &&
            !tag.name.toLowerCase().includes("unsolved"),
        )
        .map((tag) => ({ name: tag.name, value: tag.name })),
    );
  },
};
