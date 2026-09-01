import { createApp } from "./app.js";
import type { WorkerBindings } from "./bindings.js";
import { DurableObjectReminderScheduler } from "./reminders/scheduler.js";
import { D1Storage } from "./storage/d1.js";
import { loadWorkerEnv } from "./worker-env.js";

export { ReminderScheduler } from "./reminders/durable-object.js";

export default {
  fetch(
    request: Request,
    bindings: WorkerBindings,
    executionContext: ExecutionContext,
  ): Promise<Response> {
    const env = loadWorkerEnv(bindings);
    const storage = new D1Storage(bindings.DB);
    const scheduler = new DurableObjectReminderScheduler(
      bindings.REMINDER_SCHEDULER,
    );
    return Promise.resolve(
      createApp(env, storage, scheduler, executionContext).fetch(
        request,
        bindings,
        executionContext,
      ),
    );
  },

  async scheduled(
    _event: ScheduledController,
    bindings: WorkerBindings,
  ): Promise<void> {
    const storage = new D1Storage(bindings.DB);
    const scheduler = new DurableObjectReminderScheduler(
      bindings.REMINDER_SCHEDULER,
    );
    await Promise.all([
      scheduler.reconcile(),
      storage.cleanupExpired(Date.now()),
    ]);
  },
};
