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

const DISCORD_API = "https://discord.com/api/v10";
const USER_AGENT = "DiscordBot (https://github.com/sigpwny/pwnybot, 2.0.0)";
const REQUEST_TIMEOUT_MS = 10_000;
const MAX_ATTEMPTS = 3;
const MAX_RETRY_DELAY_MS = 15_000;

export class DiscordApiError extends Error {
  constructor(
    readonly status: number,
    readonly route: string,
    readonly details: string,
  ) {
    super(`Discord API request failed (${status}) for ${route}: ${details}`);
  }
}

async function discordFetch(
  env: AppEnv,
  route: string,
  init: RequestInit = {},
): Promise<Response> {
  for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt += 1) {
    let response: Response;
    try {
      response = await fetch(`${DISCORD_API}${route}`, {
        ...init,
        signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
        headers: {
          Authorization: `Bot ${env.DISCORD_BOT_TOKEN}`,
          "User-Agent": USER_AGENT,
          ...init.headers,
        },
      });
    } catch (error) {
      if (attempt === MAX_ATTEMPTS - 1) {
        throw error;
      }
      await sleep(retryDelay(attempt));
      continue;
    }

    if (response.ok) {
      return response;
    }

    const details = (await response.text()).slice(0, 1_000);
    const retryable = response.status === 429 || response.status >= 500;
    if (!retryable || attempt === MAX_ATTEMPTS - 1) {
      throw new DiscordApiError(response.status, route, details);
    }
    await sleep(
      response.status === 429
        ? rateLimitDelay(response, details)
        : retryDelay(attempt),
    );
  }
  throw new Error("Discord request retry loop exited unexpectedly");
}

function retryDelay(attempt: number): number {
  return Math.min(MAX_RETRY_DELAY_MS, 500 * 2 ** attempt);
}

function rateLimitDelay(response: Response, details: string): number {
  let seconds = Number(response.headers.get("Retry-After"));
  try {
    const body = JSON.parse(details) as { retry_after?: number };
    if (typeof body.retry_after === "number") {
      seconds = body.retry_after;
    }
  } catch {
    // Fall back to the header or exponential backoff.
  }
  return Number.isFinite(seconds)
    ? Math.min(MAX_RETRY_DELAY_MS, Math.max(0, seconds * 1_000))
    : 1_000;
}

function sleep(milliseconds: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

async function jsonRequest<T>(
  env: AppEnv,
  route: string,
  method = "GET",
  body?: unknown,
): Promise<T> {
  const response = await discordFetch(env, route, {
    method,
    headers:
      body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export async function registerGuildCommands(
  env: AppEnv,
  guildId: string,
  commands: DiscordCommandPayload[],
): Promise<void> {
  await jsonRequest(
    env,
    `/applications/${env.DISCORD_APPLICATION_ID}/guilds/${guildId}/commands`,
    "PUT",
    commands,
  );
}

export async function getCurrentUser(env: AppEnv): Promise<DiscordUser> {
  return jsonRequest(env, "/users/@me");
}

export async function getChannel(
  env: AppEnv,
  channelId: string,
): Promise<DiscordChannel> {
  return jsonRequest(env, `/channels/${channelId}`);
}

export async function listGuildChannels(
  env: AppEnv,
  guildId: string,
): Promise<DiscordChannel[]> {
  return jsonRequest(env, `/guilds/${guildId}/channels`);
}

export async function listGuildRoles(
  env: AppEnv,
  guildId: string,
): Promise<DiscordRole[]> {
  return jsonRequest(env, `/guilds/${guildId}/roles`);
}

export async function getGuildMember(
  env: AppEnv,
  guildId: string,
  userId: string,
): Promise<DiscordMember | null> {
  try {
    return await jsonRequest(env, `/guilds/${guildId}/members/${userId}`);
  } catch (error) {
    if (error instanceof DiscordApiError && error.status === 404) {
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
  return jsonRequest(
    env,
    `/guilds/${guildId}/members/search?query=${encodeURIComponent(query)}&limit=5`,
  );
}

export async function listChannelMessages(
  env: AppEnv,
  channelId: string,
  limit = 100,
): Promise<DiscordMessage[]> {
  return jsonRequest(
    env,
    `/channels/${channelId}/messages?limit=${Math.min(100, Math.max(1, limit))}`,
  );
}

export async function getChannelMessage(
  env: AppEnv,
  channelId: string,
  messageId: string,
): Promise<DiscordMessage | null> {
  try {
    return await jsonRequest(
      env,
      `/channels/${channelId}/messages/${messageId}`,
    );
  } catch (error) {
    if (error instanceof DiscordApiError && error.status === 404) {
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
  return jsonRequest(
    env,
    `/channels/${channelId}/messages/${messageId}`,
    "PATCH",
    {
      content,
    },
  );
}

export async function addGuildMemberRole(
  env: AppEnv,
  guildId: string,
  userId: string,
  roleId: string,
): Promise<void> {
  await discordFetch(
    env,
    `/guilds/${guildId}/members/${userId}/roles/${roleId}`,
    { method: "PUT" },
  );
}

export async function removeGuildMemberRole(
  env: AppEnv,
  guildId: string,
  userId: string,
  roleId: string,
): Promise<void> {
  await discordFetch(
    env,
    `/guilds/${guildId}/members/${userId}/roles/${roleId}`,
    { method: "DELETE" },
  );
}

export async function createGuildChannel(
  env: AppEnv,
  guildId: string,
  body: unknown,
): Promise<DiscordChannel> {
  return jsonRequest(env, `/guilds/${guildId}/channels`, "POST", body);
}

export async function editChannel(
  env: AppEnv,
  channelId: string,
  body: unknown,
): Promise<DiscordChannel> {
  return jsonRequest(env, `/channels/${channelId}`, "PATCH", body);
}

export async function setChannelPermission(
  env: AppEnv,
  channelId: string,
  targetId: string,
  type: 0 | 1,
  allow: string,
  deny = "0",
): Promise<void> {
  await jsonRequest(
    env,
    `/channels/${channelId}/permissions/${targetId}`,
    "PUT",
    { type, allow, deny },
  );
}

export async function addChannelPermission(
  env: AppEnv,
  channel: DiscordChannel,
  targetId: string,
  type: 0 | 1,
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
  return jsonRequest(env, `/channels/${forumId}/threads`, "POST", {
    name,
    message: { content },
    applied_tags: appliedTags,
  });
}

export async function listForumPosts(
  env: AppEnv,
  guildId: string,
  forumId: string,
): Promise<DiscordChannel[]> {
  const active = await jsonRequest<{ threads: DiscordChannel[] }>(
    env,
    `/guilds/${guildId}/threads/active`,
  );
  const archived: DiscordChannel[] = [];
  let before: string | undefined;
  while (true) {
    const query = before
      ? `?before=${encodeURIComponent(before)}&limit=100`
      : "?limit=100";
    const page = await jsonRequest<{
      threads: DiscordChannel[];
      has_more: boolean;
    }>(env, `/channels/${forumId}/threads/archived/public${query}`);
    archived.push(...page.threads);
    if (!page.has_more || page.threads.length === 0) {
      break;
    }
    before = page.threads.at(-1)?.thread_metadata?.archive_timestamp;
    if (!before) {
      break;
    }
  }
  return [...active.threads, ...archived].filter(
    (thread) => thread.parent_id === forumId,
  );
}

export async function listActiveForumPosts(
  env: AppEnv,
  guildId: string,
  forumId: string,
): Promise<DiscordChannel[]> {
  const active = await jsonRequest<{ threads: DiscordChannel[] }>(
    env,
    `/guilds/${guildId}/threads/active`,
  );
  return active.threads.filter((thread) => thread.parent_id === forumId);
}

export async function createChannelMessage(
  env: AppEnv,
  channelId: string,
  content: string,
  nonce?: string,
): Promise<DiscordMessage> {
  return jsonRequest(env, `/channels/${channelId}/messages`, "POST", {
    content,
    ...(nonce ? { nonce, enforce_nonce: true } : {}),
  });
}

export async function createDm(
  env: AppEnv,
  userId: string,
): Promise<DiscordChannel> {
  return jsonRequest(env, "/users/@me/channels", "POST", {
    recipient_id: userId,
  });
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
  await jsonRequest(
    env,
    `/webhooks/${env.DISCORD_APPLICATION_ID}/${token}/messages/@original`,
    "PATCH",
    data,
  );
}

export async function createInteractionFollowup(
  env: AppEnv,
  token: string,
  data: InteractionMessageData,
): Promise<void> {
  await jsonRequest(
    env,
    `/webhooks/${env.DISCORD_APPLICATION_ID}/${token}`,
    "POST",
    data,
  );
}

export async function editOriginalInteractionResponseWithFile(
  env: AppEnv,
  token: string,
  data: InteractionMessageData,
  filename: string,
  content: string,
): Promise<void> {
  const form = new FormData();
  form.append(
    "payload_json",
    JSON.stringify({
      ...data,
      attachments: [{ id: "0", filename }],
    }),
  );
  form.append(
    "files[0]",
    new Blob([content], { type: "text/plain;charset=utf-8" }),
    filename,
  );
  await discordFetch(
    env,
    `/webhooks/${env.DISCORD_APPLICATION_ID}/${token}/messages/@original`,
    { method: "PATCH", body: form },
  );
}
