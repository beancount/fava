import type { Completion } from "@codemirror/autocomplete";
import { snippetCompletion } from "@codemirror/autocomplete";

import { today_as_string } from "../format.ts";

export const beancount_snippets: () => readonly Completion[] = () => {
  const today = today_as_string();
  return [
    snippetCompletion(
      `${today} #{*} "#{}" "#{}"\n  #{Account:A}  #{Amount}\n  #{Account:B}`,
      {
        label: `${today} * transaction`,
      },
    ),
  ];
};
