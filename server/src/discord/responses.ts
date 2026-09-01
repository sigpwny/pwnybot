import type { InteractionMessageData } from "./types.js";

export const EPHEMERAL = 1 << 6;

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

export function pong(): Response {
  return json({ type: 1 });
}

export function message(
  data: string | InteractionMessageData,
  ephemeral = false,
): Response {
  const payload = typeof data === "string" ? { content: data } : data;
  return json({
    type: 4,
    data: {
      ...payload,
      flags: (payload.flags ?? 0) | (ephemeral ? EPHEMERAL : 0),
    },
  });
}

export function deferred(ephemeral = false): Response {
  return json({
    type: 5,
    data: { flags: ephemeral ? EPHEMERAL : 0 },
  });
}

export function deferredUpdate(): Response {
  return json({ type: 6 });
}

export function updateMessage(data: InteractionMessageData): Response {
  return json({ type: 7, data });
}

export function modal(
  customId: string,
  title: string,
  label: string,
  value = "",
): Response {
  return json({
    type: 9,
    data: {
      custom_id: customId,
      title,
      components: [
        {
          type: 1,
          components: [
            {
              type: 4,
              custom_id: "content",
              style: 2,
              label,
              value,
              required: true,
              min_length: 1,
              max_length: 2_000,
            },
          ],
        },
      ],
    },
  });
}

export function autocomplete(
  choices: Array<{ name: string; value: string | number }>,
): Response {
  return json({ type: 8, data: { choices: choices.slice(0, 25) } });
}

export function badRequest(error: string): Response {
  return json({ error }, 400);
}

export function contentTooLarge(): Response {
  return json({ error: "request_body_too_large" }, 413);
}

export function unauthorized(): Response {
  return json({ error: "invalid_request_signature" }, 401);
}
