import { Hono } from "hono";
import type { AppBindings } from "../bindings.js";
import { handleDiscordInteraction } from "../discord/interactions.js";

export const discordRoutes = new Hono<AppBindings>();

discordRoutes.post("/interactions/callback", async (context) => {
  return handleDiscordInteraction(
    context.get("env"),
    {
      env: context.get("env"),
      storage: context.get("storage"),
      scheduler: context.get("scheduler"),
      background: context.get("background"),
    },
    context.req.raw,
  );
});
