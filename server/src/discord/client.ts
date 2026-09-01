import {
  DiscordAPIError,
  HTTPError,
  REST,
  type RESTOptions,
} from "@discordjs/rest";
import {
  Routes,
  type APIChannel,
  type APIMessage,
  type APIRole,
  type APIUser,
  type RESTGetAPIChannelMessagesQuery,
  type RESTGetAPIChannelThreadsArchivedPublicResult,
  type RESTGetAPIGuildChannelsResult,
  type RESTGetAPIGuildMemberResult,
  type RESTGetAPIGuildMembersSearchQuery,
  type RESTGetAPIGuildMembersSearchResult,
  type RESTGetAPIGuildRolesResult,
  type RESTGetAPIGuildThreadsResult,
  type RESTPatchAPIChannelJSONBody,
  type RESTPatchAPIChannelMessageJSONBody,
  type RESTPatchAPIInteractionOriginalResponseJSONBody,
  type RESTPostAPICurrentUserCreateDMChannelJSONBody,
  type RESTPostAPIGuildChannelJSONBody,
  type RESTPostAPIGuildForumThreadsJSONBody,
  type RESTPostAPIChannelMessageJSONBody,
  type RESTPutAPIApplicationGuildCommandsJSONBody,
  type RESTPutAPIChannelPermissionJSONBody,
} from "discord-api-types/v10";
import type { AppEnv } from "../env.js";
import type {
  DiscordChannel,
  DiscordCommandPayload,
  DiscordMember,
  DiscordMessage,
  DiscordRole,
  DiscordUser,
  InteractionMessageData,
} from "./types.js";

const restClients = new Map<string, REST>();

function discordRest(env: AppEnv): REST {
  let client = restClients.get(env.DISCORD_BOT_TOKEN);
  if (!client) {
    client = new REST({
      version: "10",
      retries: 3,
      timeout: 10_000,
      makeRequest: fetch as unknown as RESTOptions["makeRequest"],
      userAgentAppendix: "pwnybot/2.0.0",
    }).setToken(env.DISCORD_BOT_TOKEN);
    restClients.set(env.DISCORD_BOT_TOKEN, client);
  }
  return client;
}

export function discordErrorMetadata(error: unknown): {
  status?: number;
  route?: string;
} {
  if (error instanceof DiscordAPIError || error instanceof HTTPError) {
    return { status: error.status, route: redactDiscordRoute(error.url) };
  }
  return {};
}

function redactDiscordRoute(url: string): string {
  try {
    const parsed = new URL(url);
    return parsed.pathname.replace(
      /(\/webhooks\/\d+\/)[^/]+/,
      "$1[interaction-token]",
    );
  } catch {
    return url.replace(/(\/webhooks\/\d+\/)[^/]+/, "$1[interaction-token]");
  }
}

function isNotFound(error: unknown): boolean {
  return discordErrorMetadata(error).status === 404;
}

export async function registerGuildCommands(
  env: AppEnv,
  guildId: string,
  commands: DiscordCommandPayload[],
): Promise<void> {
  await discordRest(env).put(
    Routes.applicationGuildCommands(env.DISCORD_APPLICATION_ID, guildId),
    { body: commands satisfies RESTPutAPIApplicationGuildCommandsJSONBody },
  );
}

export async function getCurrentUser(env: AppEnv): Promise<DiscordUser> {
  return (await discordRest(env).get(Routes.user())) as APIUser;
}

export async function getChannel(
  env: AppEnv,
  channelId: string,
): Promise<DiscordChannel> {
  return (await discordRest(env).get(
    Routes.channel(channelId),
  )) as DiscordChannel;
}

export async function listGuildChannels(
  env: AppEnv,
  guildId: string,
): Promise<DiscordChannel[]> {
  return (await discordRest(env).get(
    Routes.guildChannels(guildId),
  )) as RESTGetAPIGuildChannelsResult as DiscordChannel[];
}

export async function listGuildRoles(
  env: AppEnv,
  guildId: string,
): Promise<DiscordRole[]> {
  return (await discordRest(env).get(
    Routes.guildRoles(guildId),
  )) as RESTGetAPIGuildRolesResult;
}

export async function getGuildMember(
  env: AppEnv,
  guildId: string,
  userId: string,
): Promise<DiscordMember | null> {
  try {
    return (await discordRest(env).get(
      Routes.guildMember(guildId, userId),
    )) as RESTGetAPIGuildMemberResult as DiscordMember;
  } catch (error) {
    if (isNotFound(error)) {
      return null;
    }
    throw error;
  }
}

export async function searchGuildMembers(
  env: AppEnv,
  guildId: string,
  query: string,
): Promise<DiscordMember[]> {
  const search = new URLSearchParams({
    query,
    limit: "5",
  } satisfies Record<keyof RESTGetAPIGuildMembersSearchQuery, string>);
  return (await discordRest(env).get(Routes.guildMembersSearch(guildId), {
    query: search,
  })) as RESTGetAPIGuildMembersSearchResult as DiscordMember[];
}

export async function listChannelMessages(
  env: AppEnv,
  channelId: string,
  limit = 100,
): Promise<DiscordMessage[]> {
  const query = new URLSearchParams({
    limit: String(Math.min(100, Math.max(1, limit))),
  });
  return (await discordRest(env).get(Routes.channelMessages(channelId), {
    query,
  })) as APIMessage[];
}

export async function getChannelMessage(
  env: AppEnv,
  channelId: string,
  messageId: string,
): Promise<DiscordMessage | null> {
  try {
    return (await discordRest(env).get(
      Routes.channelMessage(channelId, messageId),
    )) as APIMessage;
  } catch (error) {
    if (isNotFound(error)) {
      return null;
    }
    throw error;
  }
}

export async function editChannelMessage(
  env: AppEnv,
  channelId: string,
  messageId: string,
  content: string,
): Promise<DiscordMessage> {
  const body = { content } satisfies RESTPatchAPIChannelMessageJSONBody;
  return (await discordRest(env).patch(
    Routes.channelMessage(channelId, messageId),
    { body },
  )) as APIMessage;
}

export async function addGuildMemberRole(
  env: AppEnv,
  guildId: string,
  userId: string,
  roleId: string,
): Promise<void> {
  await discordRest(env).put(Routes.guildMemberRole(guildId, userId, roleId));
}

export async function removeGuildMemberRole(
  env: AppEnv,
  guildId: string,
  userId: string,
  roleId: string,
): Promise<void> {
  await discordRest(env).delete(
    Routes.guildMemberRole(guildId, userId, roleId),
  );
}

export async function createGuildChannel(
  env: AppEnv,
  guildId: string,
  body: RESTPostAPIGuildChannelJSONBody,
): Promise<DiscordChannel> {
  return (await discordRest(env).post(Routes.guildChannels(guildId), {
    body,
  })) as DiscordChannel;
}

export async function editChannel(
  env: AppEnv,
  channelId: string,
  body: RESTPatchAPIChannelJSONBody,
): Promise<DiscordChannel> {
  return (await discordRest(env).patch(Routes.channel(channelId), {
    body,
  })) as DiscordChannel;
}

export async function setChannelPermission(
  env: AppEnv,
  channelId: string,
  targetId: string,
  type: RESTPutAPIChannelPermissionJSONBody["type"],
  allow: string,
  deny = "0",
): Promise<void> {
  const body = {
    type,
    allow,
    deny,
  } satisfies RESTPutAPIChannelPermissionJSONBody;
  await discordRest(env).put(Routes.channelPermission(channelId, targetId), {
    body,
  });
}

export async function addChannelPermission(
  env: AppEnv,
  channel: DiscordChannel,
  targetId: string,
  type: RESTPutAPIChannelPermissionJSONBody["type"],
  permission: bigint,
): Promise<void> {
  const existing = channel.permission_overwrites?.find(
    (overwrite) => overwrite.id === targetId && overwrite.type === type,
  );
  const allow = BigInt(existing?.allow ?? "0") | permission;
  const deny = BigInt(existing?.deny ?? "0") & ~permission;
  await setChannelPermission(
    env,
    channel.id,
    targetId,
    type,
    String(allow),
    String(deny),
  );
}

export async function createForumPost(
  env: AppEnv,
  forumId: string,
  name: string,
  content: string,
  appliedTags: string[] = [],
): Promise<DiscordChannel> {
  const body = {
    name,
    message: { content },
    applied_tags: appliedTags,
  } satisfies RESTPostAPIGuildForumThreadsJSONBody;
  return (await discordRest(env).post(Routes.threads(forumId), {
    body,
  })) as DiscordChannel;
}

export async function listForumPosts(
  env: AppEnv,
  guildId: string,
  forumId: string,
): Promise<DiscordChannel[]> {
  const active = (await discordRest(env).get(
    Routes.guildActiveThreads(guildId),
  )) as RESTGetAPIGuildThreadsResult;
  const archived: DiscordChannel[] = [];
  let before: string | undefined;
  while (true) {
    const query = new URLSearchParams({ limit: "100" });
    if (before) {
      query.set("before", before);
    }
    const page = (await discordRest(env).get(
      Routes.channelThreads(forumId, "public"),
      { query },
    )) as RESTGetAPIChannelThreadsArchivedPublicResult;
    archived.push(...(page.threads as DiscordChannel[]));
    if (!page.has_more || page.threads.length === 0) {
      break;
    }
    before = (page.threads.at(-1) as DiscordChannel | undefined)
      ?.thread_metadata?.archive_timestamp;
    if (!before) {
      break;
    }
  }
  return [...(active.threads as DiscordChannel[]), ...archived].filter(
    (thread) => thread.parent_id === forumId,
  );
}

export async function createChannelMessage(
  env: AppEnv,
  channelId: string,
  content: string,
  nonce?: string,
): Promise<DiscordMessage> {
  const body = {
    content,
    ...(nonce ? { nonce, enforce_nonce: true } : {}),
  } satisfies RESTPostAPIChannelMessageJSONBody;
  return (await discordRest(env).post(Routes.channelMessages(channelId), {
    body,
  })) as APIMessage;
}

export async function createDm(
  env: AppEnv,
  userId: string,
): Promise<DiscordChannel> {
  const body = {
    recipient_id: userId,
  } satisfies RESTPostAPICurrentUserCreateDMChannelJSONBody;
  return (await discordRest(env).post(Routes.userChannels(), {
    body,
  })) as APIChannel as DiscordChannel;
}

export async function pinForumPost(
  env: AppEnv,
  thread: DiscordChannel,
): Promise<void> {
  await editChannel(env, thread.id, { flags: (thread.flags ?? 0) | 2 });
}

export async function editOriginalInteractionResponse(
  env: AppEnv,
  token: string,
  data: InteractionMessageData,
): Promise<void> {
  await discordRest(env).patch(
    Routes.webhookMessage(env.DISCORD_APPLICATION_ID, token, "@original"),
    { auth: false, body: data },
  );
}

export async function createInteractionFollowup(
  env: AppEnv,
  token: string,
  data: InteractionMessageData,
): Promise<void> {
  await discordRest(env).post(
    Routes.webhook(env.DISCORD_APPLICATION_ID, token),
    { auth: false, body: data },
  );
}

export async function editOriginalInteractionResponseWithFile(
  env: AppEnv,
  token: string,
  data: InteractionMessageData,
  filename: string,
  content: string,
): Promise<void> {
  const body = {
    ...data,
    attachments: [{ id: "0", filename }],
  } satisfies RESTPatchAPIInteractionOriginalResponseJSONBody;
  await discordRest(env).patch(
    Routes.webhookMessage(env.DISCORD_APPLICATION_ID, token, "@original"),
    {
      auth: false,
      body,
      files: [
        {
          data: new TextEncoder().encode(content),
          name: filename,
          contentType: "text/plain;charset=utf-8",
        },
      ],
    },
  );
}
