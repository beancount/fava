import { test } from "uvu";
import assert from "uvu/assert";

import { Events } from "../src/lib/events";

test("register and listen to events", () => {
  const e = new Events<"t">();
  let count = 0;
  let once = 0;
  const inc = () => {
    count += 1;
  };
  e.on("t", inc);
  e.once("t", () => {
    once += 1;
  });
  assert.is(count, 0);
  assert.is(once, 0);
  e.trigger("t");
  e.trigger("t");
  e.trigger("t");
  assert.is(count, 3);
  assert.is(once, 1);
  e.remove("t", inc);
  e.trigger("t");
  assert.is(count, 3);
});

test.run();
