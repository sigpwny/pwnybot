import dotenv from "dotenv";
import { commandPayloads } from "../commands/index.js";
import { registerGuildCommands } from "../discord/client.js";
import { loadEnv } from "../env.js";

dotenv.config({ path: "../.env" });
dotenv.config({ path: ".env", override: false });

const env = loadEnv(process.env);
for (const guildId of env.GUILD_IDS) {
  await registerGuildCommands(env, guildId, commandPayloads);
  console.log(
    `Registered ${commandPayloads.length} command groups for guild ${guildId}.`,
  );
}
