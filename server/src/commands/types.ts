import type { BackgroundTasks } from "../bindings.js";
import type { AppEnv } from "../env.js";
import type { ReminderSchedulerService } from "../reminders/scheduler.js";
import type { Storage } from "../storage/types.js";
import type {
  DiscordCommandPayload,
  DiscordInteraction,
} from "../discord/types.js";

export interface CommandRuntime {
  env: AppEnv;
  storage: Storage;
  scheduler: ReminderSchedulerService;
  background: BackgroundTasks;
}

export interface CommandDefinition {
  command: DiscordCommandPayload;
  handle(
    interaction: DiscordInteraction,
    runtime: CommandRuntime,
  ): Promise<Response>;
  autocomplete?(
    interaction: DiscordInteraction,
    runtime: CommandRuntime,
  ): Promise<Response>;
}
