import { Hono } from "hono";
import type { AppBindings, BackgroundTasks } from "./bindings.js";
import type { AppEnv } from "./env.js";
import { noStore, securityHeaders, withRuntime } from "./http.js";
import type { ReminderSchedulerService } from "./reminders/scheduler.js";
import { discordRoutes } from "./routes/discord.js";
import type { Storage } from "./storage/types.js";
import { logError } from "./log.js";

export function createApp(
  env: AppEnv,
  storage: Storage,
  scheduler: ReminderSchedulerService,
  background: BackgroundTasks,
) {
  const app = new Hono<AppBindings>();

  app.use("*", withRuntime(env, storage, scheduler, background));
  app.use("*", securityHeaders);
  app.use("*", noStore);

  app.get("/", (context) =>
    context.json({ name: "pwnybot", version: "2.0.0", status: "ok" }),
  );
  app.get("/api/health", (context) => context.json({ status: "ok" }));
  app.route("/api/discord", discordRoutes);

  app.notFound((context) => context.json({ error: "not_found" }, 404));
  app.onError((error, context) => {
    logError("unhandled_api_error", error, {
      route: context.req.routePath,
    });
    return context.json({ error: "internal_error" }, 500);
  });

  return app;
}
