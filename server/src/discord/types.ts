import type {
  APIApplicationCommandInteractionDataOption,
  APIChannel,
  APIGuildForumTag,
  APIInteraction,
  APIInteractionDataResolved,
  APIInteractionGuildMember,
  APIMessage,
  APIModalSubmission,
  APIModalSubmissionComponent,
  APIOverwrite,
  APIRole,
  APIThreadMetadata,
  APIUser,
  RESTPatchAPIInteractionOriginalResponseJSONBody,
  RESTPutAPIApplicationGuildCommandsJSONBody,
  Snowflake,
} from "discord-api-types/v10";

export type DiscordUser = Pick<APIUser, "id" | "username"> & Partial<APIUser>;
export type DiscordMember = Pick<APIInteractionGuildMember, "roles"> &
  Partial<Omit<APIInteractionGuildMember, "user" | "roles">> & {
    user?: DiscordUser;
  };
export type DiscordRole = APIRole;
export type DiscordForumTag = APIGuildForumTag;
export type DiscordPermissionOverwrite = APIOverwrite;
export type DiscordMessage = APIMessage;
export type DiscordCommandOption = APIApplicationCommandInteractionDataOption &
  Partial<{
    value: string | number | boolean;
    focused: boolean;
    options: DiscordCommandOption[];
  }>;
export type DiscordComponent = APIModalSubmissionComponent &
  Partial<{
    custom_id: string;
    value: string;
    components: DiscordComponent[];
  }>;
export type DiscordCommandPayload =
  RESTPutAPIApplicationGuildCommandsJSONBody[number];
export type InteractionMessageData =
  RESTPatchAPIInteractionOriginalResponseJSONBody;

export type DiscordChannel = APIChannel &
  Partial<{
    guild_id: Snowflake;
    parent_id: Snowflake | null;
    name: string;
    flags: number;
    available_tags: APIGuildForumTag[];
    applied_tags: Snowflake[];
    permission_overwrites: APIOverwrite[];
    thread_metadata: APIThreadMetadata;
    message: APIMessage;
  }>;

/**
 * Runtime-neutral command view over Discord's interaction union. Individual
 * handlers narrow the optional data fields according to interaction type.
 */
export type DiscordInteraction = Pick<
  APIInteraction,
  "id" | "application_id" | "type" | "token"
> & {
  guild_id?: Snowflake;
  channel_id?: Snowflake;
  channel?: DiscordChannel;
  member?: DiscordMember;
  user?: APIUser;
  data?: {
    name?: string;
    options?: DiscordCommandOption[];
    custom_id?: string;
    components?: DiscordComponent[];
    resolved?: APIInteractionDataResolved;
  };
  message?: APIMessage;
};
