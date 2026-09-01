import {
  ApplicationCommandOptionType,
  ApplicationCommandType,
} from "discord-api-types/v10";
import { createInteractionFollowup } from "../discord/client.js";
import { message } from "../discord/responses.js";
import { afterInteractionAck, claimInteraction } from "./helpers.js";
import { integerOption, stringOption } from "./options.js";
import type { CommandDefinition } from "./types.js";

export const basicCommands: CommandDefinition[] = [
  {
    command: {
      name: "reverserepeat",
      type: ApplicationCommandType.ChatInput,
      description:
        "The reverserepeat command is pretty epic!! (/reverserepeat)",
      options: [
        {
          type: ApplicationCommandOptionType.String,
          name: "message",
          description: "The message",
          required: true,
        },
        {
          type: ApplicationCommandOptionType.Integer,
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
      type: ApplicationCommandType.ChatInput,
      description: "No Description Set",
      options: [
        {
          type: ApplicationCommandOptionType.Subcommand,
          name: "say",
          description: "The message command is pretty epic!! (/template say)",
          options: [
            {
              type: ApplicationCommandOptionType.String,
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
