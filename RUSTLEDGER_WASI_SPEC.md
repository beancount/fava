# Rustledger WASI Interface Specification for Fava

This document specifies the WASI interface that rustledger needs to expose for Fava integration.

## Overview

Fava requires these core capabilities from rustledger:
1. **Parse** beancount source (with include resolution) → entries + errors + options
2. **Query** entries using BQL → columns + rows
3. **Format** entries back to beancount syntax
4. **Validate** source files

## WASI Export Functions

All functions use simple string I/O with JSON for complex data structures.

### 1. `parse(source: string) -> string`

Parse beancount source and return a JSON result.

**Input**: Beancount source as a string (includes already resolved by Python layer)

**Output** (JSON):
```json
{
  "entries": [Directive...],
  "errors": [BeancountError...],
  "options": LedgerOptions
}
```

### 2. `query(entries_json: string, options_json: string, query_string: string) -> string`

Run a BQL query against parsed entries.

**Inputs**:
- `entries_json`: JSON array of directives (from parse output)
- `options_json`: JSON object of ledger options (from parse output)
- `query_string`: BQL query string

**Output** (JSON):
```json
{
  "columns": [
    {"name": "account", "datatype": "str"},
    {"name": "balance", "datatype": "Inventory"}
  ],
  "rows": [
    ["Assets:Bank", {"USD": "1000.00", "EUR": "500.00"}],
    ...
  ],
  "errors": []
}
```

### 3. `format_entry(entry_json: string, indent: int, currency_column: int) -> string`

Format a single entry back to beancount syntax.

**Input**: JSON directive, indentation spaces, currency alignment column

**Output**: Formatted beancount string

### 4. `validate(source: string) -> string`

Validate beancount source and return detailed errors.

**Output** (JSON):
```json
{
  "valid": true,
  "errors": [BeancountError...]
}
```

### 5. `version() -> string`

Return rustledger version string.

---

## Data Structures (JSON Schema)

### Directive Types

All directives share these base fields:
```json
{
  "type": "transaction|balance|open|close|...",
  "date": "2024-01-15",
  "meta": {
    "filename": "/path/to/file.beancount",
    "lineno": 42,
    "custom_key": "custom_value"
  }
}
```

**CRITICAL**: The `meta.filename` and `meta.lineno` fields are required for Fava's editing functionality.

#### Transaction
```json
{
  "type": "transaction",
  "date": "2024-01-15",
  "flag": "*",
  "payee": "Coffee Shop",
  "narration": "Morning coffee",
  "tags": ["food"],
  "links": ["receipt-123"],
  "postings": [Posting...],
  "meta": {...}
}
```

#### Posting
```json
{
  "account": "Expenses:Food",
  "units": {"number": "5.00", "currency": "USD"},
  "cost": {
    "number": "4.50",
    "currency": "USD",
    "date": "2024-01-10",
    "label": "lot1"
  },
  "price": {"number": "1.10", "currency": "EUR"},
  "flag": null,
  "meta": {}
}
```

Note: `units`, `cost`, and `price` can be `null` for auto-computed values.

#### Balance
```json
{
  "type": "balance",
  "date": "2024-01-15",
  "account": "Assets:Bank",
  "amount": {"number": "1000.00", "currency": "USD"},
  "tolerance": "0.015",
  "diff_amount": null,
  "meta": {...}
}
```

`diff_amount` is non-null when the balance check failed.

#### Open
```json
{
  "type": "open",
  "date": "2024-01-01",
  "account": "Assets:Bank",
  "currencies": ["USD", "EUR"],
  "booking": "FIFO",
  "meta": {...}
}
```

`booking` is one of: `"STRICT"`, `"FIFO"`, `"LIFO"`, `"HIFO"`, `"AVERAGE"`, `"NONE"`, or `null`.

#### Close
```json
{
  "type": "close",
  "date": "2024-12-31",
  "account": "Assets:OldBank",
  "meta": {...}
}
```

#### Price
```json
{
  "type": "price",
  "date": "2024-01-15",
  "currency": "EUR",
  "amount": {"number": "1.08", "currency": "USD"},
  "meta": {...}
}
```

#### Event
```json
{
  "type": "event",
  "date": "2024-01-15",
  "event_type": "location",
  "description": "New York",
  "meta": {...}
}
```

#### Note
```json
{
  "type": "note",
  "date": "2024-01-15",
  "account": "Assets:Bank",
  "comment": "Called customer service",
  "tags": [],
  "links": [],
  "meta": {...}
}
```

#### Document
```json
{
  "type": "document",
  "date": "2024-01-15",
  "account": "Assets:Bank",
  "filename": "/path/to/statement.pdf",
  "tags": [],
  "links": [],
  "meta": {...}
}
```

#### Pad
```json
{
  "type": "pad",
  "date": "2024-01-01",
  "account": "Assets:Bank",
  "source_account": "Equity:Opening-Balances",
  "meta": {...}
}
```

#### Commodity
```json
{
  "type": "commodity",
  "date": "2024-01-01",
  "currency": "USD",
  "meta": {...}
}
```

#### Query (stored query)
```json
{
  "type": "query",
  "date": "2024-01-01",
  "name": "monthly_expenses",
  "query_string": "SELECT account, sum(position) WHERE ...",
  "meta": {...}
}
```

#### Custom
```json
{
  "type": "custom",
  "date": "2024-01-01",
  "custom_type": "fava-option",
  "values": ["indent", "4"],
  "meta": {...}
}
```

### Amount
```json
{
  "number": "1234.56",
  "currency": "USD"
}
```

Numbers are strings to preserve precision (Decimal).

### Cost
```json
{
  "number": "100.00",
  "currency": "USD",
  "date": "2024-01-01",
  "label": "lot-identifier"
}
```

All fields except `currency` can be `null`.

### BeancountError
```json
{
  "message": "Invalid account name",
  "source": {
    "filename": "/path/to/file.beancount",
    "lineno": 42
  },
  "severity": "error"
}
```

`severity` is one of: `"error"`, `"warning"`.

### LedgerOptions

These options are needed by Fava:

```json
{
  "title": "My Ledger",
  "filename": "/path/to/main.beancount",

  "name_assets": "Assets",
  "name_liabilities": "Liabilities",
  "name_equity": "Equity",
  "name_income": "Income",
  "name_expenses": "Expenses",

  "account_current_conversions": "Equity:Conversions:Current",
  "account_current_earnings": "Equity:Earnings:Current",
  "account_previous_balances": "Equity:Opening-Balances",
  "account_previous_conversions": "Equity:Conversions:Previous",
  "account_previous_earnings": "Equity:Earnings:Previous",
  "account_rounding": null,
  "account_unrealized_gains": "Income:Unrealized",

  "booking_method": "STRICT",
  "commodities": ["USD", "EUR", "AAPL"],
  "conversion_currency": "",
  "documents": ["documents"],
  "include": ["/path/to/main.beancount", "/path/to/included.beancount"],
  "operating_currency": ["USD"],
  "render_commas": true,

  "inferred_tolerance_default": {},
  "inferred_tolerance_multiplier": "0.5",
  "infer_tolerance_from_cost": false,
  "tolerance_multiplier": "1.0",

  "input_hash": "sha256hash..."
}
```

### Query Column Types

For the query `columns` array, these are the possible `datatype` values Fava handles:

| datatype | Description | Row value format |
|----------|-------------|------------------|
| `"str"` | String | `"value"` |
| `"int"` | Integer | `123` |
| `"Decimal"` | Decimal number | `"1234.56"` |
| `"bool"` | Boolean | `true`/`false` |
| `"date"` | Date | `"2024-01-15"` |
| `"set"` | Set of strings | `["tag1", "tag2"]` |
| `"object"` | Any object | JSON object |
| `"Amount"` | Amount | `{"number": "100", "currency": "USD"}` |
| `"Position"` | Position | `{"units": Amount, "cost": Cost}` |
| `"Inventory"` | Inventory | `{"USD": "100.00", "EUR": "50.00"}` |

---

## Python-Side Responsibilities

These operations will be handled in Python, not WASI:

### 1. Include Resolution

Python reads files and resolves `include` directives before passing concatenated source to rustledger:

```python
def resolve_includes(main_file: str) -> tuple[str, list[str]]:
    """
    Returns (concatenated_source, list_of_included_files)
    """
    # Parse includes from source
    # Read each included file
    # Concatenate with markers for filename/lineno tracking
```

### 2. File I/O

All file reading/writing stays in Python. Rustledger only processes strings.

### 3. Encryption Detection

Fava uses `beancount.utils.encryption.is_encrypted_file()` - this stays in Python.

### 4. Python Plugin Support

Python beancount plugins won't work with rustledger. This is a known limitation.

---

## WASI Memory/String Interface

For wasmtime-py integration, rustledger should export standard WASI string passing:

```rust
// Rust side - standard WASI component model exports
#[no_mangle]
pub extern "C" fn parse(source_ptr: *const u8, source_len: usize) -> *mut c_char {
    // Parse and return JSON string
}

#[no_mangle]
pub extern "C" fn free_string(ptr: *mut c_char) {
    // Free returned string
}
```

Or use wasi-component-model for cleaner interface with `wit` definitions.

---

## Testing Interface

Suggest adding a simple test function:

### `test_parse(source: string) -> string`

```json
{
  "success": true,
  "entry_count": 42,
  "error_count": 0,
  "parse_time_ms": 5.2
}
```

---

## Performance Considerations

1. **Stateful ParsedLedger**: For repeated queries on the same data, consider keeping parsed state in WASI linear memory and providing:
   - `create_ledger(source) -> ledger_id`
   - `query_ledger(ledger_id, query) -> result`
   - `destroy_ledger(ledger_id)`

2. **Incremental Updates**: Future enhancement - allow partial re-parsing when only some files change.

---

## Questions for Rustledger Maintainer

1. **Include handling**: Should rustledger's WASI build handle includes itself (given WASI filesystem access), or should Python pre-resolve?

2. **Query compatibility**: Does rustledger's BQL support all beanquery features? Known gaps?

3. **Booking method**: Does rustledger fully implement all booking methods (FIFO, LIFO, HIFO, AVERAGE)?

4. **Decimal precision**: What precision is used for numbers? Beancount uses Python's Decimal (arbitrary precision).

5. **Plugin system**: Any plans for WASM-based plugins to replace Python plugins?
