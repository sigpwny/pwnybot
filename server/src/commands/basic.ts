import { createInteractionFollowup } from "../discord/client.js";
import { message } from "../discord/responses.js";
import { afterInteractionAck, claimInteraction } from "./helpers.js";
import { integerOption, stringOption } from "./options.js";
import type { CommandDefinition } from "./types.js";

const CHAT_INPUT = 1;
const STRING = 3;
const INTEGER = 4;
const GUILD_CONTEXT = 0;
const GUILD_INSTALL = 0;

export const basicCommands: CommandDefinition[] = [
  {
    command: {
      name: "reverserepeat",
      type: CHAT_INPUT,
      description:
        "The reverserepeat command is pretty epic!! (/reverserepeat)",
      contexts: [GUILD_CONTEXT],
      integration_types: [GUILD_INSTALL],
      options: [
        {
          type: STRING,
          name: "message",
          description: "The message",
          required: true,
        },
        {
          type: INTEGER,
          name: "times",
          description: "# of times max 3",
          required: false,
          min_value: 1,
          max_value: 3,
        },
      ],
    },
    async handle(interaction, runtime) {
      const content = Array.from(stringOption(interaction, "message"))
        .reverse()
        .join("");
      const times = integerOption(interaction, "times", 1);
      if (times > 1) {
        runtime.background.waitUntil(
          (async () => {
            await afterInteractionAck();
            if (!(await claimInteraction(interaction, runtime))) {
              return;
            }
            for (let index = 1; index < times; index += 1) {
              await createInteractionFollowup(runtime.env, interaction.token, {
                content,
              });
            }
          })(),
        );
      }
      return message(content);
    },
  },
  {
    command: {
      name: "template",
      type: CHAT_INPUT,
      description: "No Description Set",
      contexts: [GUILD_CONTEXT],
      integration_types: [GUILD_INSTALL],
      options: [
        {
          type: 1,
          name: "say",
          description: "The message command is pretty epic!! (/template say)",
          options: [
            {
              type: STRING,
              name: "message",
              description: "The message",
              required: true,
            },
          ],
        },
      ],
    },
    async handle(interaction) {
      return message(stringOption(interaction, "message"));
    },
  },
];
