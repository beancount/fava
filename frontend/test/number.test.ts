import { equal, ok } from "node:assert/strict";
import { test } from "node:test";

import { evaluate_number_expression } from "../src/lib/number.ts";

test("number: normalizes plain numbers while preserving decimal precision", () => {
  const cases: [string, string][] = [
    ["10", "10"],
    ["-5", "-5"],
    ["+5", "5"],
    ["10.00", "10.00"],
    ["-10.20", "-10.20"],
    ["  10.00  ", "10.00"],
    ["1,234.50", "1234.50"],
    ["1,00,000", "100000"],
    [".25", "0.25"],
    ["-.25", "-0.25"],
    ["+.5", "0.5"],
    ["10.", "10"],
    ["-10.", "-10"],
    ["0", "0"],
    ["-0", "0"],
    ["-0.", "0"],
    ["-0.00", "0.00"],
    ["0010.50", "10.50"],
  ];

  for (const [input, expected] of cases) {
    const res = evaluate_number_expression(input);
    ok(res.is_ok, `Expected ok for ${JSON.stringify(input)}`);
    equal(res.value, expected);
  }
});

test("number: evaluates arithmetic expressions with exact rational precision", () => {
  const cases: [string, string][] = [
    ["(10 + 0.25)", "10.25"],
    ["0.1 + 0.2", "0.3"],
    ["2 + 3 * 4", "14"],
    ["10 - 3 - 2", "5"],
    ["12 / 3 / 2", "2"],
    ["-5 + 2", "-3"],
    ["-(1 + 2)", "-3"],
    ["+(2 + 3)", "5"],
    ["--3", "3"],
    ["+-+-3", "3"],
    ["((1 + 2) * (3 + 4)) / 3", "7"],
    ["(1 / 3) * 3", "1"],
    ["1 / 3", "0.333333333333"],
    ["2 / 3", "0.666666666667"],
    ["1 / -2", "-0.5"],
    ["-1 / -2", "0.5"],
    ["-(5 - 5)", "0"],
    ["-0 + 0", "0"],
    ["-1 / 30000000000000", "0"],
    ["-5 + 5", "0"],
    ["1,000 + 2,500.50", "3500.5"],
    ["(10 + 20) * .25", "7.5"],
    ["1000000000000000000000 * 2", "2000000000000000000000"],
    ["1 / 10000000000000000", "0.0000000000000001"],
    ["2999999999999 / 3000000000000", "1"],
    ["  ( 1  +  2 ) * 3  ", "9"],
    [`${"(".repeat(100)}1${")".repeat(100)}`, "1"],
  ];

  for (const [input, expected] of cases) {
    const res = evaluate_number_expression(input);
    ok(res.is_ok, `Expected ok for ${JSON.stringify(input)}`);
    equal(res.value, expected);
  }
});

test("number: rejects invalid expressions and division by zero", () => {
  const invalid_cases = [
    "",
    "   ",
    "1 / 0",
    "1 / (2 - 2)",
    "(1 + 2",
    "1 + 2)",
    "1 + * 2",
    "2 * (1 / 0)",
    "()",
    "( )",
    "1,,000",
    "1,",
    ",5",
    "1.2,3",
    "1..2",
    "1.2.3",
    ".",
    "-.",
    "1 + .",
    "(1)(2)",
    "1 +",
    "+",
    "-",
    "abc",
    "1e5",
    `${"(".repeat(101)}1${")".repeat(101)}`,
  ];

  for (const input of invalid_cases) {
    const res = evaluate_number_expression(input);
    ok(res.is_err, `Expected err for ${JSON.stringify(input)}`);
  }

  const div_zero = evaluate_number_expression("1 / 0");
  ok(div_zero.is_err);
  equal(div_zero.error, "Division by zero");
});
