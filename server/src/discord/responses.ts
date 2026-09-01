import {
  ComponentType,
  InteractionResponseType,
  MessageFlags,
  TextInputStyle,
} from "discord-api-types/v10";
import type { InteractionMessageData } from "./types.js";

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

export function pong(): Response {
  return json({ type: InteractionResponseType.Pong });
}

export function message(
  data: string | InteractionMessageData,
  ephemeral = false,
): Response {
  const payload = typeof data === "string" ? { content: data } : data;
  return json({
    type: InteractionResponseType.ChannelMessageWithSource,
    data: {
      ...payload,
      flags: (payload.flags ?? 0) | (ephemeral ? MessageFlags.Ephemeral : 0),
    },
  });
}

export function deferred(ephemeral = false): Response {
  return json({
    type: InteractionResponseType.DeferredChannelMessageWithSource,
    data: { flags: ephemeral ? MessageFlags.Ephemeral : 0 },
  });
}

export function deferredUpdate(): Response {
  return json({ type: InteractionResponseType.DeferredMessageUpdate });
}

export function updateMessage(data: InteractionMessageData): Response {
  return json({ type: InteractionResponseType.UpdateMessage, data });
}

export function modal(
  customId: string,
  title: string,
  label: string,
  value = "",
): Response {
  return json({
    type: InteractionResponseType.Modal,
    data: {
      custom_id: customId,
      title,
      components: [
        {
          type: ComponentType.ActionRow,
          components: [
            {
              type: ComponentType.TextInput,
              custom_id: "content",
              style: TextInputStyle.Paragraph,
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
  return json({
    type: InteractionResponseType.ApplicationCommandAutocompleteResult,
    data: { choices: choices.slice(0, 25) },
  });
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
