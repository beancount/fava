import type { Completion } from "@codemirror/autocomplete";
import { snippetCompletion } from "@codemirror/autocomplete";

import { todayAsString } from "../format";

export const beancountSnippets: () => readonly Completion[] = () => {
  const today = todayAsString();
  return [
    snippetCompletion(
      `${today} #{*} "#{}" "#{}"\n  #{Account:A}  #{Amount}\n  #{Account:B}`,
      {
        label: `${today} * transaction`,
      },
    ),
  ];
};
