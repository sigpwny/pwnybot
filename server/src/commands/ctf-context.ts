import { ChannelType } from "discord-api-types/v10";
import { getChannel } from "../discord/client.js";
import type { AppEnv } from "../env.js";
import type { DiscordChannel } from "../discord/types.js";
import type { DiscordInteraction } from "../discord/types.js";

export interface CtfContext {
  post: DiscordChannel;
  forum: DiscordChannel;
}

export async function getCtfContext(
  env: AppEnv,
  interaction: DiscordInteraction,
  completePost = false,
): Promise<CtfContext | null> {
  if (!interaction.channel_id) {
    return null;
  }
  const post =
    !completePost && interaction.channel?.parent_id
      ? interaction.channel
      : await getChannel(env, interaction.channel_id);
  if (!post.parent_id) {
    return null;
  }
  const forum = await getChannel(env, post.parent_id);
  if (
    forum.type !== ChannelType.GuildForum ||
    !forum.name?.startsWith("ctf-")
  ) {
    return null;
  }
  return { post, forum };
}
