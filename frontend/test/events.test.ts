import test from "ava";
import { Events } from "../src/lib/events";

test("register and listen to events", (t) => {
  const e = new Events<"t">();
  let count = 0;
  let once = 0;
  const inc = (): void => {
    count += 1;
  };
  e.on("t", inc);
  e.once("t", () => {
    once += 1;
  });
  t.deepEqual(count, 0);
  t.deepEqual(once, 0);
  e.trigger("t");
  e.trigger("t");
  e.trigger("t");
  t.deepEqual(count, 3);
  t.deepEqual(once, 1);
  e.remove("t", inc);
  e.trigger("t");
  t.deepEqual(count, 3);
});
