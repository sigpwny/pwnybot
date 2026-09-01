# pwnybot

The official SIGPwny Discord bot. Version 2 is a TypeScript rewrite built around Discord HTTP interactions, with Cloudflare Workers and D1 as the default runtime. The same Hono application can run on Node.js with SQLite when a conventional server is required.

## Architecture

- `server/src/app.ts` is the runtime-neutral Hono application.
- `server/src/worker.ts` is the Cloudflare Workers entrypoint.
- `server/src/node.ts` is the self-hosted Node.js entrypoint.
- `server/src/commands/` keeps each command declaration beside its handler.
- `server/src/storage/` provides D1, SQLite, and in-memory adapters behind one asynchronous interface.
- `server/src/reminders/` delivers D1 reminders through a singleton Durable Object alarm. Node uses the same delivery code with an in-process timer.
- Discord state such as forums, challenges, roles, and messages remains in Discord. Only reminders are stored locally.

No Discord Gateway process or Python runtime is required.

## Compatibility

The initial v2 port includes:

- `/reverserepeat`
- `/template say`
- `/chal create` and `/chal solve`
- `/ctf create`, `/ctf addcategory`, and `/ctf addrole`
- `/ctfs optin` and `/ctfs optout`
- `/roles add` and `/roles remove`, including autocomplete
- `/manager assign_roles`
- `/manager say` with ephemeral Confirm/Cancel buttons
- `/manager edit` with direct modal input
- `/copypasta byid`, `/copypasta byname`, and `/copypasta random`
- `/reminders create`, `/reminders list`, and `/reminders delete`

The v1 reaction watcher has been replaced by authenticated HTTP interactions. No Gateway connection is used.

## Development

Prerequisites:

- Node.js 22 or newer
- npm
- A Discord application with a bot user

```bash
cp .env.example .env
cd server
npm install
npm run typecheck
npm test
```

Register commands after filling in `.env`:

```bash
npm run discord:commands:register
```

Discord must send interactions to:

```text
https://<hostname>/api/discord/interactions/callback
```

See the deployment guides:

- [Cloudflare Workers and D1](docs/deployment/cloudflare-workers.md)
- [Self-hosted Node and SQLite](docs/deployment/self-hosted.md)

## Configuration

| Variable | Purpose |
| --- | --- |
| `DISCORD_APPLICATION_ID` | Discord application ID |
| `DISCORD_BOT_TOKEN` | Bot token used for Discord REST requests |
| `DISCORD_PUBLIC_KEY` | Ed25519 public key used to verify interactions |
| `GUILD_IDS` | Comma-separated guild IDs for command registration |
| `CTF_CATEGORY_CHANNELS` | Comma-separated candidate parent category IDs |
| `CTF_ROLES` | Comma-separated CTF team role IDs |
| `UIUC_ROLES` | Comma-separated UIUC verification role IDs |
| `MODERATOR_ROLES` | Comma-separated reminder moderator role IDs |
| `PRIVATE_ROLES` | JSON array of `{ "name", "discord_role_id" }` objects |

Node additionally accepts `PORT` and `SQLITE_PATH`.

V1 `config.yml` is not loaded by v2. Convert its `private_roles` array to the `PRIVATE_ROLES` JSON environment variable before cutover. Existing PostgreSQL reminders must be drained or migrated separately; v2 does not discard the old Docker volume automatically.

Use `npm run db:import:postgres` for a non-destructive reminder migration. See the deployment guides for target-specific commands.

## Reliability

- Discord side effects are deduplicated by interaction ID for 24 hours.
- Temporary component and pagination state is owner, guild, and channel bound.
- Discord REST requests use bounded timeouts and retries for network, rate-limit, and server failures.
- Failed reminders retry five times with exponential backoff, then are deleted and logged.
- Runtime errors are emitted as structured metadata without tokens or message content.

## Verification

```bash
cd server
npm run format:check
npm run typecheck
npm test
npm run build
npx wrangler deploy --dry-run
```
