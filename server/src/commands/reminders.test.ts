import assert from "node:assert/strict";
import test from "node:test";
import { parseDuration } from "./reminders.js";

test("parseDuration preserves the v1 unit grammar", () => {
  assert.equal(parseDuration("1w2d3h4m5s"), 788_645_000);
  assert.equal(parseDuration("10m"), 600_000);
  assert.equal(parseDuration(""), 0);
  assert.equal(parseDuration("1h30m"), 5_400_000);
});

test("parseDuration rejects out-of-order and unsupported values", () => {
  assert.equal(parseDuration("30m1h"), null);
  assert.equal(parseDuration("1H"), null);
  assert.equal(parseDuration("-1m"), null);
  assert.equal(parseDuration("1.5h"), null);
});
