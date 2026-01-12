import { deepEqual } from "node:assert/strict";
import { test } from "node:test";

import { build_compressed_sources_tree } from "../src/lib/sources.ts";

test("sources: buildSourcesTree (unix path separator)", () => {
  const empty = build_compressed_sources_tree(new Set<string>());
  deepEqual(empty, { name: "", path: "", children: [] });

  const root = build_compressed_sources_tree(new Set<string>(["/main.bean"]));
  deepEqual(root, {
    name: "/",
    path: "/",
    children: [{ name: "main.bean", path: "/main.bean", children: [] }],
  });

  const one = build_compressed_sources_tree(
    new Set<string>(["/data/main.bean"]),
  );
  deepEqual(one, {
    name: "/data/",
    path: "/data/",
    children: [{ name: "main.bean", path: "/data/main.bean", children: [] }],
  });

  const two = build_compressed_sources_tree(
    new Set<string>(["/data/main.bean", "/data/other.bean"]),
  );
  deepEqual(two, {
    name: "/data/",
    path: "/data/",
    children: [
      { name: "main.bean", path: "/data/main.bean", children: [] },
      { name: "other.bean", path: "/data/other.bean", children: [] },
    ],
  });

  const complex = build_compressed_sources_tree(
    new Set<string>([
      "/home/data/main.bean",
      "/home/data/deep_include.bean",
      "/home/data/deep/include/data.bean",
      "/home/data/include.bean",
      "/home/data/include/data1.bean",
      "/home/data/include/data2.bean",
      "/home/data/other.bean",
    ]),
  );
  deepEqual(complex, {
    name: "/home/data/",
    path: "/home/data/",
    children: [
      { name: "main.bean", path: "/home/data/main.bean", children: [] },
      {
        name: "deep_include.bean",
        path: "/home/data/deep_include.bean",
        children: [],
      },
      {
        name: "deep/include/",
        path: "/home/data/deep/include/",
        children: [
          {
            name: "data.bean",
            path: "/home/data/deep/include/data.bean",
            children: [],
          },
        ],
      },
      { name: "include.bean", path: "/home/data/include.bean", children: [] },
      {
        name: "include/",
        path: "/home/data/include/",
        children: [
          {
            name: "data1.bean",
            path: "/home/data/include/data1.bean",
            children: [],
          },
          {
            name: "data2.bean",
            path: "/home/data/include/data2.bean",
            children: [],
          },
        ],
      },
      { name: "other.bean", path: "/home/data/other.bean", children: [] },
    ],
  });
});

test("sources: buildSourcesTree (windows path separator)", () => {
  const root = build_compressed_sources_tree(
    new Set<string>(["C:\\main.bean"]),
  );
  deepEqual(root, {
    name: "C:\\",
    path: "C:\\",
    children: [{ name: "main.bean", path: "C:\\main.bean", children: [] }],
  });

  const one = build_compressed_sources_tree(
    new Set<string>(["C:\\data\\main.bean"]),
  );
  deepEqual(one, {
    name: "C:\\data\\",
    path: "C:\\data\\",
    children: [
      { name: "main.bean", path: "C:\\data\\main.bean", children: [] },
    ],
  });

  const two = build_compressed_sources_tree(
    new Set<string>(["C:\\data\\main.bean", "C:\\data\\other.bean"]),
  );
  deepEqual(two, {
    name: "C:\\data\\",
    path: "C:\\data\\",
    children: [
      { name: "main.bean", path: "C:\\data\\main.bean", children: [] },
      { name: "other.bean", path: "C:\\data\\other.bean", children: [] },
    ],
  });

  const complex = build_compressed_sources_tree(
    new Set<string>([
      "C:\\home\\data\\main.bean",
      "C:\\home\\data\\deep_include.bean",
      "C:\\home\\data\\deep\\include\\data.bean",
      "C:\\home\\data\\include.bean",
      "C:\\home\\data\\include\\data1.bean",
      "C:\\home\\data\\include\\data2.bean",
      "C:\\home\\data\\other.bean",
    ]),
  );
  deepEqual(complex, {
    name: "C:\\home\\data\\",
    path: "C:\\home\\data\\",
    children: [
      { name: "main.bean", path: "C:\\home\\data\\main.bean", children: [] },
      {
        name: "deep_include.bean",
        path: "C:\\home\\data\\deep_include.bean",
        children: [],
      },
      {
        name: "deep\\include\\",
        path: "C:\\home\\data\\deep\\include\\",
        children: [
          {
            name: "data.bean",
            path: "C:\\home\\data\\deep\\include\\data.bean",
            children: [],
          },
        ],
      },
      {
        name: "include.bean",
        path: "C:\\home\\data\\include.bean",
        children: [],
      },
      {
        name: "include\\",
        path: "C:\\home\\data\\include\\",
        children: [
          {
            name: "data1.bean",
            path: "C:\\home\\data\\include\\data1.bean",
            children: [],
          },
          {
            name: "data2.bean",
            path: "C:\\home\\data\\include\\data2.bean",
            children: [],
          },
        ],
      },
      { name: "other.bean", path: "C:\\home\\data\\other.bean", children: [] },
    ],
  });
});

test("sources: buildSourcesTree (mixed path separator)", () => {
  const one = build_compressed_sources_tree(
    new Set<string>(["C:\\data/main.bean"]),
  );
  deepEqual(one, {
    name: "C:\\data/",
    path: "C:\\data/",
    children: [{ name: "main.bean", path: "C:\\data/main.bean", children: [] }],
  });

  const two = build_compressed_sources_tree(
    new Set<string>(["C:\\data/main.bean", "C:\\data/other.bean"]),
  );
  deepEqual(two, {
    name: "C:\\data/",
    path: "C:\\data/",
    children: [
      { name: "main.bean", path: "C:\\data/main.bean", children: [] },
      { name: "other.bean", path: "C:\\data/other.bean", children: [] },
    ],
  });

  const complex = build_compressed_sources_tree(
    new Set<string>([
      "C:\\home\\data/main.bean",
      "C:\\home\\data/deep_include.bean",
      "C:\\home\\data/deep\\include\\data.bean",
      "C:\\home\\data/include.bean",
      "C:\\home\\data/include\\data1.bean",
      "C:\\home\\data/include\\data2.bean",
      "C:\\home\\data/other.bean",
    ]),
  );
  deepEqual(complex, {
    name: "C:\\home\\data/",
    path: "C:\\home\\data/",
    children: [
      { name: "main.bean", path: "C:\\home\\data/main.bean", children: [] },
      {
        name: "deep_include.bean",
        path: "C:\\home\\data/deep_include.bean",
        children: [],
      },
      {
        name: "deep\\include\\",
        path: "C:\\home\\data/deep\\include\\",
        children: [
          {
            name: "data.bean",
            path: "C:\\home\\data/deep\\include\\data.bean",
            children: [],
          },
        ],
      },
      {
        name: "include.bean",
        path: "C:\\home\\data/include.bean",
        children: [],
      },
      {
        name: "include\\",
        path: "C:\\home\\data/include\\",
        children: [
          {
            name: "data1.bean",
            path: "C:\\home\\data/include\\data1.bean",
            children: [],
          },
          {
            name: "data2.bean",
            path: "C:\\home\\data/include\\data2.bean",
            children: [],
          },
        ],
      },
      { name: "other.bean", path: "C:\\home\\data/other.bean", children: [] },
    ],
  });
});
