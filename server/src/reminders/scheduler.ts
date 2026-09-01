import type { AppEnv } from "../env.js";
import type { Storage } from "../storage/types.js";
import { deliverDueReminders } from "./delivery.js";
import { logError } from "../log.js";

export interface ReminderSchedulerService {
  schedule(remindAt: number): Promise<void>;
  reconcile(): Promise<void>;
}

export class DurableObjectReminderScheduler implements ReminderSchedulerService {
  constructor(private readonly namespace: DurableObjectNamespace) {}

  private stub(): DurableObjectStub {
    return this.namespace.get(this.namespace.idFromName("scheduler"));
  }

  async schedule(remindAt: number): Promise<void> {
    await this.stub().fetch("https://reminder-scheduler/schedule", {
      method: "POST",
      body: String(remindAt),
    });
  }

  async reconcile(): Promise<void> {
    await this.stub().fetch("https://reminder-scheduler/reconcile", {
      method: "POST",
    });
  }
}

export class TimerReminderScheduler implements ReminderSchedulerService {
  private timer?: NodeJS.Timeout;
  private scheduledAt?: number;

  constructor(
    private readonly storage: Storage,
    private readonly env: AppEnv,
  ) {}

  async schedule(remindAt: number): Promise<void> {
    if (this.scheduledAt !== undefined && this.scheduledAt <= remindAt) {
      return;
    }
    this.arm(remindAt);
  }

  async reconcile(): Promise<void> {
    const nextAt = await this.storage.nextReminderAt();
    if (nextAt === null) {
      if (this.timer) {
        clearTimeout(this.timer);
      }
      this.timer = undefined;
      this.scheduledAt = undefined;
      return;
    }
    this.arm(nextAt);
  }

  private arm(remindAt: number): void {
    if (this.timer) {
      clearTimeout(this.timer);
    }
    this.scheduledAt = remindAt;
    const delay = Math.max(0, Math.min(remindAt - Date.now(), 2_147_483_647));
    this.timer = setTimeout(() => {
      this.timer = undefined;
      this.scheduledAt = undefined;
      deliverDueReminders(this.storage, this.env)
        .then(() => this.reconcile())
        .catch((error) => {
          logError("reminder_scheduler_failed", error);
          this.arm(Date.now() + 5_000);
        });
    }, delay);
    this.timer.unref();
  }
}
