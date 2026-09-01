import nacl from "tweetnacl";
import type { CommandRuntime } from "../commands/types.js";
import { dispatchCommand } from "../commands/index.js";
import type { AppEnv } from "../env.js";
import {
  badRequest,
  contentTooLarge,
  message,
  pong,
  unauthorized,
} from "./responses.js";
import type { DiscordInteraction } from "./types.js";
import { logInteractionError } from "../log.js";

const MAX_BODY_BYTES = 64 * 1024;
const MAX_SIGNATURE_AGE_MS = 5 * 60 * 1_000;

function hexBytes(value: string): Uint8Array | null {
  if (!/^[0-9a-f]+$/i.test(value) || value.length % 2 !== 0) {
    return null;
  }
  return Uint8Array.from(value.match(/.{2}/g) ?? [], (byte) =>
    Number.parseInt(byte, 16),
  );
}

async function readBody(request: Request): Promise<string | null> {
  const contentLength = Number(request.headers.get("Content-Length") ?? 0);
  if (contentLength > MAX_BODY_BYTES) {
    return null;
  }

  if (!request.body) {
    return "";
  }

  const reader = request.body.getReader();
  const chunks: Uint8Array[] = [];
  let size = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    size += value.byteLength;
    if (size > MAX_BODY_BYTES) {
      await reader.cancel();
      return null;
    }
    chunks.push(value);
  }

  const body = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) {
    body.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return new TextDecoder().decode(body);
}

function verify(env: AppEnv, request: Request, rawBody: string): boolean {
  const signature = request.headers.get("X-Signature-Ed25519");
  const timestamp = request.headers.get("X-Signature-Timestamp");
  if (!signature || !timestamp) {
    return false;
  }
  const timestampMs = Number(timestamp) * 1_000;
  if (
    !Number.isFinite(timestampMs) ||
    Math.abs(Date.now() - timestampMs) > MAX_SIGNATURE_AGE_MS
  ) {
    return false;
  }
  const signatureBytes = hexBytes(signature);
  const keyBytes = hexBytes(env.DISCORD_PUBLIC_KEY);
  return Boolean(
    signatureBytes &&
    signatureBytes.length === nacl.sign.signatureLength &&
    keyBytes &&
    keyBytes.length === nacl.sign.publicKeyLength &&
    nacl.sign.detached.verify(
      new TextEncoder().encode(timestamp + rawBody),
      signatureBytes,
      keyBytes,
    ),
  );
}

export async function handleDiscordInteraction(
  env: AppEnv,
  runtime: CommandRuntime,
  request: Request,
): Promise<Response> {
  const rawBody = await readBody(request);
  if (rawBody === null) {
    return contentTooLarge();
  }
  if (!verify(env, request, rawBody)) {
    return unauthorized();
  }

  let interaction: DiscordInteraction;
  try {
    interaction = JSON.parse(rawBody) as DiscordInteraction;
  } catch {
    return badRequest("invalid_json");
  }

  if (interaction.type === 1) {
    return pong();
  }
  if (![2, 3, 4, 5].includes(interaction.type)) {
    return badRequest("unsupported_interaction_type");
  }

  try {
    return await dispatchCommand(interaction, runtime);
  } catch (error) {
    logInteractionError("interaction_failed", interaction, error);
    return message(":x: An error has occured.");
  }
}
