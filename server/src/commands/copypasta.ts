import { autocomplete, message } from "../discord/responses.js";
import copypastas from "./copypasta-data.json" with { type: "json" };
import {
  focusedOption,
  integerOption,
  stringOption,
  subcommand,
} from "./options.js";
import type { CommandDefinition } from "./types.js";

export const copypastaCommand: CommandDefinition = {
  command: {
    name: "copypasta",
    type: 1,
    description: "No Description Set",
    contexts: [0],
    integration_types: [0],
    options: [
      {
        type: 1,
        name: "byid",
        description: "copypasta by id",
        options: [
          { type: 4, name: "id", description: "copypasta id", required: true },
        ],
      },
      {
        type: 1,
        name: "byname",
        description: "copypasta by name",
        options: [
          {
            type: 3,
            name: "name",
            description: "copypasta name",
            required: true,
            autocomplete: true,
          },
        ],
      },
      { type: 1, name: "random", description: "random copypasta" },
    ],
  },
  async handle(interaction) {
    const name = subcommand(interaction)?.name;
    const item =
      name === "byid"
        ? copypastas.find(
            (candidate) => candidate.id === integerOption(interaction, "id"),
          )
        : name === "byname"
          ? copypastas.find(
              (candidate) =>
                candidate.name.toLowerCase() ===
                stringOption(interaction, "name").toLowerCase(),
            )
          : copypastas[Math.floor(Math.random() * copypastas.length)];
    return message(item?.copypasta ?? "Not Found");
  },
  async autocomplete(interaction) {
    const current = String(focusedOption(interaction)?.value ?? "");
    return autocomplete(
      copypastas
        .filter((item) =>
          item.name.toLowerCase().includes(current.toLowerCase()),
        )
        .map((item) => ({ name: item.name, value: item.name })),
    );
  },
};
