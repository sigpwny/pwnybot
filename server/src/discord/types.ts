export interface DiscordUser {
  id: string;
  username: string;
  global_name?: string | null;
}

export interface DiscordMember {
  user?: DiscordUser;
  roles: string[];
  permissions?: string;
}

export interface DiscordRole {
  id: string;
  name: string;
}

export interface DiscordForumTag {
  id: string;
  name: string;
  moderated?: boolean;
  emoji_id?: string | null;
  emoji_name?: string | null;
}

export interface DiscordChannel {
  id: string;
  guild_id?: string;
  parent_id?: string | null;
  name?: string;
  type: number;
  flags?: number;
  archived?: boolean;
  available_tags?: DiscordForumTag[];
  applied_tags?: string[];
  permission_overwrites?: DiscordPermissionOverwrite[];
  thread_metadata?: {
    archive_timestamp: string;
  };
  message?: { id: string };
}

export interface DiscordPermissionOverwrite {
  id: string;
  type: 0 | 1;
  allow: string;
  deny: string;
}

export interface DiscordMessage {
  id: string;
  content: string;
  author: DiscordUser;
  embeds?: unknown[];
}

export interface DiscordCommandOption {
  name: string;
  type: number;
  value?: string | number | boolean;
  focused?: boolean;
  options?: DiscordCommandOption[];
}

export interface DiscordInteraction {
  id: string;
  application_id: string;
  type: number;
  token: string;
  guild_id?: string;
  channel_id?: string;
  channel?: DiscordChannel;
  member?: DiscordMember;
  user?: DiscordUser;
  data?: {
    name?: string;
    options?: DiscordCommandOption[];
    custom_id?: string;
    components?: DiscordComponent[];
    resolved?: {
      users?: Record<string, DiscordUser>;
      members?: Record<string, DiscordMember>;
      roles?: Record<string, DiscordRole>;
      channels?: Record<string, DiscordChannel>;
    };
  };
  message?: DiscordMessage & { components?: DiscordComponent[] };
}

export interface DiscordComponent {
  type: number;
  custom_id?: string;
  value?: string;
  components?: DiscordComponent[];
}

export interface DiscordCommandPayload {
  name: string;
  type: number;
  description?: string;
  default_member_permissions?: string;
  contexts?: number[];
  integration_types?: number[];
  options?: unknown[];
}

export interface InteractionMessageData {
  content?: string;
  embeds?: unknown[];
  flags?: number;
  allowed_mentions?: unknown;
  components?: unknown[];
  attachments?: unknown[];
}
