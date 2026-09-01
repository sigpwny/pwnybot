# Cloudflare Workers and D1

Cloudflare Workers is the default pwnybot v2 target. Discord sends signed HTTP interactions to the Worker, D1 stores reminders, and a singleton Durable Object alarm wakes at the next reminder time.

## Prerequisites

- Cloudflare account
- Node.js 22 or newer
- Discord application and bot token
- A public hostname, either a `workers.dev` URL or a custom Worker route

## Discord Setup

Collect these values from the Discord Developer Portal:

- Application ID
- Bot token
- Public key

Set the Interactions Endpoint URL to:

```text
https://<worker-host>/api/discord/interactions/callback
```

The bot does not connect to the Discord Gateway and does not require Message Content Intent.

## D1 Setup

From `server/`:

```bash
npm install
npx wrangler d1 create pwnybot
```

Replace `database_id` in `server/wrangler.jsonc` with the returned ID, then apply migrations:

```bash
npm run db:migrate:remote
```

## Bindings

Set the bot token as a Worker secret:

```bash
npx wrangler secret put DISCORD_BOT_TOKEN
```

Add non-secret configuration under `vars` in `server/wrangler.jsonc`, or inject equivalent bindings from deployment automation:

```jsonc
"vars": {
  "DISCORD_APPLICATION_ID": "...",
  "DISCORD_PUBLIC_KEY": "...",
  "GUILD_IDS": "...",
  "CTF_CATEGORY_CHANNELS": "...",
  "CTF_ROLES": "...",
  "UIUC_ROLES": "...",
  "MODERATOR_ROLES": "...",
  "PRIVATE_ROLES": "[]"
}
```

Do not commit a real bot token.

## Deploy

```bash
cd server
npm run typecheck
npm test
npm run worker:deploy
npm run discord:commands:register
```

The command registration script reads the repository-root `.env`. Discord guild commands update immediately in the configured guilds.

Registration uses Discord's bulk guild-command endpoint. `/manager say` uses ephemeral buttons and `/manager edit` uses a modal; neither requires a Gateway process.

## Reminder Scheduling

Creating a reminder commits its row to D1 and asks the `ReminderScheduler` Durable Object to move its alarm to the earliest due time. The alarm claims due rows with leases, sends messages through Discord REST, records failures for retry, and arms itself for the next row.

A 15-minute Cron Trigger only reconciles the alarm. It is not the primary delivery loop and performs no repeated reminder polling. This repairs scheduling if a reminder was committed but the subsequent Durable Object request failed.

Cloudflare alarms provide at-least-once execution. Delivery uses stable Discord nonces and leased rows to reduce duplicates, but consumers should not assume mathematically exact-once delivery across every network failure.

## Existing PostgreSQL Reminders

D1 migrations create a new reminder database. To import v1 PostgreSQL rows non-destructively:

```bash
cd server
POSTGRES_URL='postgresql://...' \
CLOUDFLARE_ACCOUNT_ID='...' \
CLOUDFLARE_API_TOKEN='...' \
D1_DATABASE_ID='...' \
npm run db:import:postgres -- --target d1
```

The importer preserves reminder IDs and timestamps, accepts matching rows when safely resumed, refuses conflicting IDs, verifies every imported ID, and never changes source rows. Stop v1 reminder creation/delivery during the final import and do not run v1 and v2 against the same logical reminders. The reconciliation Cron Trigger arms the Durable Object after import; allow up to 15 minutes or deploy immediately afterward.

## GitHub Deployment

`.github/workflows/deploy-cloudflare.yml` is the primary production workflow. Configure:

- Secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `DISCORD_BOT_TOKEN`
- Variables: `D1_DATABASE_ID`, `DISCORD_APPLICATION_ID`, `DISCORD_PUBLIC_KEY`, `GUILD_IDS`, `CTF_CATEGORY_CHANNELS`, `CTF_ROLES`, `UIUC_ROLES`, `MODERATOR_ROLES`, `PRIVATE_ROLES`

The workflow typechecks and tests, applies D1 migrations, deploys the Worker, persists the bot-token secret, and bulk-registers guild commands. On the first deployment there can be a brief interval between Worker creation and secret upload; configure the Discord endpoint after the workflow completes.
