import type { WorkerBindings } from "./bindings.js";
import { loadEnv, type AppEnv } from "./env.js";

export function loadWorkerEnv(bindings: WorkerBindings): AppEnv {
  return loadEnv({
    DISCORD_APPLICATION_ID: bindings.DISCORD_APPLICATION_ID,
    DISCORD_BOT_TOKEN: bindings.DISCORD_BOT_TOKEN,
    DISCORD_TOKEN: bindings.DISCORD_TOKEN,
    DISCORD_PUBLIC_KEY: bindings.DISCORD_PUBLIC_KEY,
    GUILD_IDS: bindings.GUILD_IDS,
    CTF_CATEGORY_CHANNELS: bindings.CTF_CATEGORY_CHANNELS,
    CTF_ROLES: bindings.CTF_ROLES,
    UIUC_ROLES: bindings.UIUC_ROLES,
    MODERATOR_ROLES: bindings.MODERATOR_ROLES,
    PRIVATE_ROLES: bindings.PRIVATE_ROLES,
    PORT: bindings.PORT,
  });
}
