import type { Result } from "./result.ts";
import { err, ok } from "./result.ts";

const PLAIN_NUMBER_RE = /^[+-]?(?:\d+(?:,\d+)*(?:\.\d*)?|\.\d+)$/;
const NUMBER_TOKEN_RE = /(?:\d+(?:,\d+)*(?:\.\d*)?|\.\d+)/y;
const WHITESPACE_RE = /\s+/y;
const MAX_PAREN_DEPTH = 100;
const MAX_FRACTION_DIGITS = 12;

interface Rational {
  readonly num: bigint;
  readonly den: bigint;
}

function gcd(a: bigint, b: bigint): bigint {
  let x = a < 0n ? -a : a;
  let y = b < 0n ? -b : b;
  while (y !== 0n) {
    const t = x % y;
    x = y;
    y = t;
  }
  return x;
}

function make_rational(raw_num: bigint, raw_den: bigint): Rational {
  if (raw_num === 0n) {
    return { num: 0n, den: 1n };
  }
  const signed_num = raw_den < 0n ? -raw_num : raw_num;
  const pos_den = raw_den < 0n ? -raw_den : raw_den;
  const abs_num = signed_num < 0n ? -signed_num : signed_num;
  const divisor = gcd(abs_num, pos_den);
  return { num: signed_num / divisor, den: pos_den / divisor };
}

function add_rational(a: Rational, b: Rational): Rational {
  return make_rational(a.num * b.den + b.num * a.den, a.den * b.den);
}

function sub_rational(a: Rational, b: Rational): Rational {
  return make_rational(a.num * b.den - b.num * a.den, a.den * b.den);
}

function mul_rational(a: Rational, b: Rational): Rational {
  return make_rational(a.num * b.num, a.den * b.den);
}

function div_rational(a: Rational, b: Rational): Result<Rational, string> {
  if (b.num === 0n) {
    return err("Division by zero");
  }
  return ok(make_rational(a.num * b.den, a.den * b.num));
}

/**
 * Normalize a single plain number while keeping explicit trailing decimal
 * zeros so Beancount's inferred decimal tolerance is preserved.
 */
function normalize_plain_number(trimmed: string): string {
  let sign = "";
  let body = trimmed;
  if (body.startsWith("-")) {
    sign = "-";
    body = body.slice(1);
  } else if (body.startsWith("+")) {
    body = body.slice(1);
  }
  body = body.replace(/,/g, "");
  if (body.startsWith(".")) {
    body = `0${body}`;
  }
  if (body.endsWith(".")) {
    body = body.slice(0, -1);
  }
  body = body.replace(/^0+(?=\d)/, "");
  if (sign === "-" && !/[1-9]/.test(body)) {
    sign = "";
  }
  return `${sign}${body}`;
}

function parse_number_literal(raw: string): Rational {
  const clean = raw.replace(/,/g, "");
  const dot_index = clean.indexOf(".");
  if (dot_index === -1) {
    return { num: BigInt(clean), den: 1n };
  }
  const int_part = clean.slice(0, dot_index);
  const frac_part = clean.slice(dot_index + 1);
  return make_rational(
    BigInt(`${int_part}${frac_part}`),
    10n ** BigInt(frac_part.length),
  );
}

function format_scaled_decimal(
  sign: string,
  scaled: bigint,
  scale: number,
): string {
  if (scaled === 0n) {
    return "0";
  }
  if (scale === 0) {
    return `${sign}${scaled.toString()}`;
  }
  const digits = scaled.toString().padStart(scale + 1, "0");
  const split_index = digits.length - scale;
  const int_part = digits.slice(0, split_index);
  const frac_part = digits.slice(split_index).replace(/0+$/, "");
  if (frac_part.length === 0) {
    return `${sign}${int_part}`;
  }
  return `${sign}${int_part}.${frac_part}`;
}

function format_rational(value: Rational): string {
  if (value.num === 0n) {
    return "0";
  }
  const sign = value.num < 0n ? "-" : "";
  const abs_num = value.num < 0n ? -value.num : value.num;

  let rem = value.den;
  let c2 = 0;
  while (rem % 2n === 0n) {
    rem /= 2n;
    c2 += 1;
  }
  let c5 = 0;
  while (rem % 5n === 0n) {
    rem /= 5n;
    c5 += 1;
  }

  if (rem === 1n) {
    const scale = Math.max(c2, c5);
    const scaled =
      abs_num * 2n ** BigInt(scale - c2) * 5n ** BigInt(scale - c5);
    return format_scaled_decimal(sign, scaled, scale);
  }

  const factor = 10n ** BigInt(MAX_FRACTION_DIGITS);
  const rounded = (abs_num * factor * 2n + value.den) / (2n * value.den);
  return format_scaled_decimal(sign, rounded, MAX_FRACTION_DIGITS);
}

class ExpressionParser {
  readonly #input: string;
  #pos = 0;
  #depth = 0;

  constructor(input: string) {
    this.#input = input;
  }

  parse(): Result<Rational, string> {
    const res = this.#parse_expr();
    if (res.is_err) {
      return res;
    }
    this.#skip_whitespace();
    if (this.#pos < this.#input.length) {
      return err(`Unexpected character '${this.#input[this.#pos] ?? ""}'`);
    }
    return res;
  }

  #skip_whitespace(): void {
    WHITESPACE_RE.lastIndex = this.#pos;
    if (WHITESPACE_RE.test(this.#input)) {
      this.#pos = WHITESPACE_RE.lastIndex;
    }
  }

  #parse_expr(): Result<Rational, string> {
    const left_res = this.#parse_term();
    if (left_res.is_err) {
      return left_res;
    }
    let acc = left_res.value;
    while (this.#pos < this.#input.length) {
      this.#skip_whitespace();
      const op = this.#input[this.#pos];
      if (op !== "+" && op !== "-") {
        break;
      }
      this.#pos += 1;
      const right_res = this.#parse_term();
      if (right_res.is_err) {
        return right_res;
      }
      acc =
        op === "+"
          ? add_rational(acc, right_res.value)
          : sub_rational(acc, right_res.value);
    }
    return ok(acc);
  }

  #parse_term(): Result<Rational, string> {
    const left_res = this.#parse_unary();
    if (left_res.is_err) {
      return left_res;
    }
    let acc = left_res.value;
    while (this.#pos < this.#input.length) {
      this.#skip_whitespace();
      const op = this.#input[this.#pos];
      if (op !== "*" && op !== "/") {
        break;
      }
      this.#pos += 1;
      const right_res = this.#parse_unary();
      if (right_res.is_err) {
        return right_res;
      }
      if (op === "*") {
        acc = mul_rational(acc, right_res.value);
      } else {
        const div_res = div_rational(acc, right_res.value);
        if (div_res.is_err) {
          return div_res;
        }
        acc = div_res.value;
      }
    }
    return ok(acc);
  }

  #parse_unary(): Result<Rational, string> {
    let negative = false;
    while (this.#pos < this.#input.length) {
      this.#skip_whitespace();
      const op = this.#input[this.#pos];
      if (op === "+") {
        this.#pos += 1;
      } else if (op === "-") {
        this.#pos += 1;
        negative = !negative;
      } else {
        break;
      }
    }
    const primary_res = this.#parse_primary();
    if (primary_res.is_err) {
      return primary_res;
    }
    if (negative && primary_res.value.num !== 0n) {
      return ok({
        num: -primary_res.value.num,
        den: primary_res.value.den,
      });
    }
    return primary_res;
  }

  #parse_primary(): Result<Rational, string> {
    this.#skip_whitespace();
    if (this.#pos >= this.#input.length) {
      return err("Unexpected end of expression");
    }
    const ch = this.#input[this.#pos];
    if (ch === "(") {
      if (this.#depth >= MAX_PAREN_DEPTH) {
        return err("Maximum parenthesis depth exceeded");
      }
      this.#pos += 1;
      this.#depth += 1;
      const inner_res = this.#parse_expr();
      this.#depth -= 1;
      if (inner_res.is_err) {
        return inner_res;
      }
      this.#skip_whitespace();
      if (this.#input[this.#pos] !== ")") {
        return err("Expected closing parenthesis");
      }
      this.#pos += 1;
      return inner_res;
    }
    NUMBER_TOKEN_RE.lastIndex = this.#pos;
    const match = NUMBER_TOKEN_RE.exec(this.#input);
    if (match === null) {
      return err(`Unexpected character '${ch ?? ""}'`);
    }
    this.#pos = NUMBER_TOKEN_RE.lastIndex;
    return ok(parse_number_literal(match[0]));
  }
}

/**
 * Evaluate a plain number or arithmetic expression into a decimal string.
 */
export function evaluate_number_expression(
  input: string,
): Result<string, string> {
  const trimmed = input.trim();
  if (trimmed.length === 0) {
    return err("Empty expression");
  }
  if (PLAIN_NUMBER_RE.test(trimmed)) {
    return ok(normalize_plain_number(trimmed));
  }
  return new ExpressionParser(trimmed).parse().map(format_rational);
}
