import type { WorkerBindings } from "../bindings.js";
import { loadWorkerEnv } from "../worker-env.js";
import { D1Storage } from "../storage/d1.js";
import { deliverDueReminders } from "./delivery.js";
import { logError } from "../log.js";

export class ReminderScheduler {
  constructor(
    private readonly state: DurableObjectState,
    private readonly bindings: WorkerBindings,
  ) {}

  async fetch(request: Request): Promise<Response> {
    const pathname = new URL(request.url).pathname;
    if (
      request.method !== "POST" ||
      !["/schedule", "/reconcile"].includes(pathname)
    ) {
      return new Response("Not found", { status: 404 });
    }

    const storage = new D1Storage(this.bindings.DB);
    if (pathname === "/schedule") {
      const requestedAt = Number(await request.text());
      if (!Number.isFinite(requestedAt)) {
        return new Response("Invalid reminder time", { status: 400 });
      }
      const current = await this.state.storage.getAlarm();
      if (current === null || requestedAt < current) {
        await this.state.storage.setAlarm(Math.max(Date.now(), requestedAt));
      }
    } else {
      await this.armNext(storage);
    }
    return new Response(null, { status: 204 });
  }

  async alarm(): Promise<void> {
    const storage = new D1Storage(this.bindings.DB);
    try {
      await deliverDueReminders(storage, loadWorkerEnv(this.bindings));
      await this.armNext(storage);
    } catch (error) {
      logError("reminder_alarm_failed", error);
      await this.state.storage.setAlarm(Date.now() + 60_000);
    }
  }

  private async armNext(storage: D1Storage): Promise<void> {
    const nextAt = await storage.nextReminderAt();
    if (nextAt === null) {
      await this.state.storage.deleteAlarm();
      return;
    }
    await this.state.storage.setAlarm(Math.max(Date.now(), nextAt));
  }
}
