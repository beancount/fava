import { equal } from "node:assert/strict";
import { test } from "node:test";

import { has_current_mtime, set_mtime } from "../src/stores/mtime.ts";

test("mtime - track whether a load has data for the current mtime", () => {
  const { signal } = new AbortController();
  equal(has_current_mtime(signal), false);
  set_mtime("9000000000000000001", signal);
  equal(has_current_mtime(signal), true);

  // A change seen elsewhere, e.g., when polling for changes.
  set_mtime("9000000000000000002");
  equal(has_current_mtime(signal), false);
  // The oldest response counts if there are multiple ones for a load.
  set_mtime("9000000000000000002", signal);
  equal(has_current_mtime(signal), false);

  const { signal: restarted } = new AbortController();
  set_mtime("9000000000000000002", restarted);
  equal(has_current_mtime(restarted), true);
});
