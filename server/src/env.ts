export interface PrivateRole {
  name: string;
  discordRoleId: string;
}

export interface AppEnv {
  DISCORD_APPLICATION_ID: string;
  DISCORD_BOT_TOKEN: string;
  DISCORD_PUBLIC_KEY: string;
  GUILD_IDS: string[];
  CTF_CATEGORY_CHANNELS: string[];
  CTF_ROLES: string[];
  UIUC_ROLES: string[];
  MODERATOR_ROLES: string[];
  PRIVATE_ROLES: PrivateRole[];
  PORT: number;
}

type EnvSource = Record<string, string | undefined>;

const SNOWFLAKE = /^\d{17,20}$/;

function requireValue(source: EnvSource, name: string): string {
  const value = source[name]?.trim();
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

function parseSnowflakeList(value: string | undefined, name: string): string[] {
  const values = (value ?? "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  for (const value of values) {
    if (!SNOWFLAKE.test(value)) {
      throw new Error(`${name} contains an invalid Discord ID: ${value}`);
    }
  }
  return values;
}

function parsePrivateRoles(value: string | undefined): PrivateRole[] {
  if (!value) {
    return [];
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(value);
  } catch {
    throw new Error("PRIVATE_ROLES must be a JSON array");
  }

  if (!Array.isArray(parsed)) {
    throw new Error("PRIVATE_ROLES must be a JSON array");
  }

  const roles = parsed.map((entry, index) => {
    if (!entry || typeof entry !== "object") {
      throw new Error(`PRIVATE_ROLES[${index}] must be an object`);
    }
    const candidate = entry as Record<string, unknown>;
    const name = candidate.name;
    const discordRoleId = candidate.discord_role_id ?? candidate.discordRoleId;
    if (
      typeof name !== "string" ||
      !name ||
      typeof discordRoleId !== "string" ||
      !SNOWFLAKE.test(discordRoleId)
    ) {
      throw new Error(
        `PRIVATE_ROLES[${index}] must have a name and valid discord_role_id`,
      );
    }
    return { name, discordRoleId };
  });
  const names = new Set<string>();
  for (const role of roles) {
    const normalized = role.name.toLowerCase();
    if (names.has(normalized)) {
      throw new Error(
        `PRIVATE_ROLES contains ambiguous names that differ only by case: ${role.name}`,
      );
    }
    names.add(normalized);
  }
  return roles;
}

export function loadEnv(source: EnvSource): AppEnv {
  const applicationId = requireValue(source, "DISCORD_APPLICATION_ID");
  if (!SNOWFLAKE.test(applicationId)) {
    throw new Error("DISCORD_APPLICATION_ID must be a Discord snowflake");
  }

  const publicKey = requireValue(source, "DISCORD_PUBLIC_KEY");
  if (!/^[0-9a-f]{64}$/i.test(publicKey)) {
    throw new Error("DISCORD_PUBLIC_KEY must be a 32-byte hexadecimal key");
  }

  const guildIds = parseSnowflakeList(source.GUILD_IDS, "GUILD_IDS");
  if (guildIds.length === 0) {
    throw new Error("GUILD_IDS must contain at least one Discord guild ID");
  }

  const port = Number(source.PORT ?? 8787);
  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    throw new Error("PORT must be an integer from 1 to 65535");
  }

  return {
    DISCORD_APPLICATION_ID: applicationId,
    DISCORD_BOT_TOKEN:
      source.DISCORD_BOT_TOKEN?.trim() || requireValue(source, "DISCORD_TOKEN"),
    DISCORD_PUBLIC_KEY: publicKey,
    GUILD_IDS: guildIds,
    CTF_CATEGORY_CHANNELS: parseSnowflakeList(
      source.CTF_CATEGORY_CHANNELS,
      "CTF_CATEGORY_CHANNELS",
    ),
    CTF_ROLES: parseSnowflakeList(source.CTF_ROLES, "CTF_ROLES"),
    UIUC_ROLES: parseSnowflakeList(source.UIUC_ROLES, "UIUC_ROLES"),
    MODERATOR_ROLES: parseSnowflakeList(
      source.MODERATOR_ROLES,
      "MODERATOR_ROLES",
    ),
    PRIVATE_ROLES: parsePrivateRoles(source.PRIVATE_ROLES),
    PORT: port,
  };
}
