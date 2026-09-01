# Improvement Decisions

The reviewed serverless-native improvements are implemented in v2.

## Implemented

1. `/manager say` retains latest-message lookup and uses an ephemeral, authenticated 60-second Confirm/Cancel flow.
2. `/manager edit` accepts replacement text in a modal and verifies that the target message belongs to the bot.
3. Gateway presence is permanently removed.
4. Reminder `silent` is a native optional boolean.
5. Durable Object alarms provide reminder timing; D1 is authoritative and Cron repairs scheduling.
6. Reminder delivery retries five times with capped exponential backoff, then deletes and logs the reminder.
7. Administrators or configured moderators can manage reminders.
8. Reminder lists use owner-bound ephemeral pagination.
9. Side-effecting interactions are deduplicated by interaction ID.
10. Discord REST requests have bounded timeouts and retry network, 429, and 5xx failures.
11. Large mass-role results use concise counts and a text attachment when needed.
12. Runtime failures use structured metadata-only logs.
13. Roles, CTF categories, usernames, and copypasta names match case-insensitively.
14. Case-only duplicate private-role names are rejected during configuration loading.
15. Custom CTF categories containing `unsolved` are rejected.
16. Partially initialized CTF forums are retained and reported for manual repair.
17. V1's unrestricted mention parsing is preserved.
18. CTF opt-in adds missing roles; opt-out removes all configured CTF roles.
19. A non-destructive PostgreSQL-to-D1/SQLite reminder importer preserves IDs and timestamps and verifies imports.
20. Cloudflare deployment is automated first; self-host deployment remains manual.
21. Command registration remains guild-scoped for the initial rollout.

Forum permission overwrites and generic public errors were already completed during the initial rewrite.
