# Self-Hosted Node and SQLite

The self-hosted runtime uses the same Hono application and command handlers as Cloudflare Workers. SQLite replaces D1 and an in-process timer replaces Durable Object alarms.

## Configure

Copy `.env.example` to `.env` and fill in Discord and guild values. Configure the Discord Interactions Endpoint URL as:

```text
https://<hostname>/api/discord/interactions/callback
```

The endpoint must be available over HTTPS. Put Caddy, nginx, or another reverse proxy in front of port `8787`.

## Run with Node

```bash
cd server
npm install
npm run build
npm run start
```

The default SQLite path is `server/data/local.sqlite` when commands are run from `server/`. Unapplied migrations run at startup.

## Run with Docker Compose

From the repository root:

```bash
docker compose up --build -d pwnybot
```

The Compose service publishes `127.0.0.1:8787` and persists SQLite in the `pwnybot_data` volume. Configure a host reverse proxy to forward the public HTTPS callback route.

The legacy PostgreSQL volume is not deleted, but v2 does not read it directly. Import pending reminders before replacing the v1 service:

```bash
cd server
POSTGRES_URL='postgresql://...' \
npm run db:import:postgres -- --target sqlite --sqlite-path data/local.sqlite
```

The importer preserves IDs and timestamps, accepts matching rows when safely resumed, refuses conflicting IDs, verifies every imported ID, and never changes source rows. Stop v1 reminder creation/delivery during the final import. The legacy `deploy.sh` path requires `V2_CUTOVER_APPROVED=true` to make that decision explicit.

For the existing GitHub deployment workflow, set the `V2_CUTOVER_APPROVED` repository secret to `true` only after completing that cutover check.

## Register Commands

From `server/`:

```bash
npm run discord:commands:register
```

Registration uses Discord's bulk guild-command endpoint. `/manager say` uses ephemeral buttons and `/manager edit` uses a modal; neither requires a Gateway process.

## Reminder Scheduling

At startup, the Node runtime reads the earliest reminder and arms one timer. Delivery and retry behavior is shared with the Worker runtime. No one-second polling loop is used.

Run only one self-hosted pwnybot process per SQLite file. Horizontal replicas require a shared storage adapter and a distributed scheduler.
