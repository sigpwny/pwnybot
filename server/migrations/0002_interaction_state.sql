CREATE TABLE IF NOT EXISTS interaction_states (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  owner_user_id TEXT NOT NULL,
  guild_id TEXT NOT NULL,
  channel_id TEXT NOT NULL,
  payload TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  expires_at INTEGER NOT NULL,
  consumed_at INTEGER
);

CREATE INDEX IF NOT EXISTS interaction_states_expiry_idx
  ON interaction_states (expires_at);

CREATE TABLE IF NOT EXISTS processed_interactions (
  id TEXT PRIMARY KEY,
  expires_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS processed_interactions_expiry_idx
  ON processed_interactions (expires_at);
