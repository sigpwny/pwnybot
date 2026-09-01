import type { MiddlewareHandler } from "hono";
import type { AppBindings, BackgroundTasks } from "./bindings.js";
import type { AppEnv } from "./env.js";
import type { ReminderSchedulerService } from "./reminders/scheduler.js";
import type { Storage } from "./storage/types.js";

export function withRuntime(
  env: AppEnv,
  storage: Storage,
  scheduler: ReminderSchedulerService,
  background: BackgroundTasks,
): MiddlewareHandler<AppBindings> {
  return async (context, next) => {
    context.set("env", env);
    context.set("storage", storage);
    context.set("scheduler", scheduler);
    context.set("background", background);
    await next();
  };
}

export const securityHeaders: MiddlewareHandler = async (context, next) => {
  await next();
  context.header("X-Content-Type-Options", "nosniff");
  context.header("Referrer-Policy", "no-referrer");
  context.header(
    "Content-Security-Policy",
    "default-src 'none'; frame-ancestors 'none'",
  );
};

export const noStore: MiddlewareHandler = async (context, next) => {
  await next();
  context.header("Cache-Control", "no-store");
};
