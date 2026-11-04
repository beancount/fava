import { equal, ok } from "node:assert/strict";
import { test } from "node:test";

import { Tooltip } from "../src/charts/tooltip.ts";
import { setup_jsdom } from "./dom.ts";

test.beforeEach(setup_jsdom);

/** Set up a chart in a bordered, scrollable article inside the viewport. */
function chart_tooltip(t: test.TestContext) {
  t.mock.getter(document.documentElement, "clientWidth", () => 500);
  t.mock.getter(document.documentElement, "clientHeight", () => 400);
  const article = document.querySelector("article");
  ok(article);
  t.mock.method(
    article,
    "getBoundingClientRect",
    () => new DOMRect(100, 50, 370, 300),
  );
  t.mock.getter(article, "clientLeft", () => 2);
  t.mock.getter(article, "clientTop", () => 2);
  t.mock.getter(article, "clientWidth", () => 350);
  t.mock.getter(article, "clientHeight", () => 280);
  const wrapper = document.createElement("div");
  article.appendChild(wrapper);
  const tooltip = new Tooltip();
  tooltip.init(wrapper);
  const div = wrapper.querySelector("div");
  ok(div);
  return { tooltip, div, wrapper, article };
}

test("tooltips stay out of layout until positioned and after hiding", (t) => {
  const { tooltip, div } = chart_tooltip(t);
  equal(div.hidden, true);
  tooltip.content(["a value"]);
  equal(div.hidden, true);
  tooltip.position(200, 150);
  equal(div.hidden, false);
  tooltip.hide();
  equal(div.hidden, true);
  tooltip.position(200, 150);
  equal(div.hidden, false);
  equal(div.textContent, "a value");
});

test("tooltips keep chart coordinates when they fit", (t) => {
  const { tooltip, div } = chart_tooltip(t);
  t.mock.method(
    div,
    "getBoundingClientRect",
    () => new DOMRect(200, 100, 100, 60),
  );
  tooltip.position(200.2, 150.7);
  equal(div.style.left, "200px");
  equal(div.style.top, "151px");
});

test("tooltips stop at the article client edge, excluding borders and scrollbars", (t) => {
  const { tooltip, div } = chart_tooltip(t);
  t.mock.method(
    div,
    "getBoundingClientRect",
    () => new DOMRect(400, 100, 100, 60),
  );
  tooltip.position(350, 150);
  // The client edge is 100 + 2 + 350 = 452, not the border-box edge 470.
  equal(div.style.left, "302px");
  equal(div.style.getPropertyValue("--tooltip-max-width"), "350px");
});

test("tooltips stay inside the viewport when the article is partially outside it", (t) => {
  const { tooltip, div, article } = chart_tooltip(t);
  t.mock.method(
    article,
    "getBoundingClientRect",
    () => new DOMRect(-40, 50, 370, 300),
  );
  t.mock.method(
    div,
    "getBoundingClientRect",
    () => new DOMRect(-20, 100, 100, 60),
  );
  tooltip.position(30, 150);
  equal(div.style.left, "50px");
  equal(div.style.getPropertyValue("--tooltip-max-width"), "312px");
});

test("tooltips outside an article use the viewport bounds", (t) => {
  const { tooltip, div, wrapper } = chart_tooltip(t);
  document.body.appendChild(wrapper);
  t.mock.method(
    div,
    "getBoundingClientRect",
    () => new DOMRect(450, 100, 100, 60),
  );
  tooltip.position(300, 150);
  equal(div.style.left, "250px");
  equal(div.style.getPropertyValue("--tooltip-max-width"), "500px");
});

test("tooltips are hidden if the article is outside the viewport", (t) => {
  const { tooltip, div, article } = chart_tooltip(t);
  t.mock.method(
    article,
    "getBoundingClientRect",
    () => new DOMRect(600, 50, 370, 300),
  );
  tooltip.position(200, 150);
  equal(div.hidden, true);
});
