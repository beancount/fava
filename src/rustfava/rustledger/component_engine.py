"""Rustledger engine backed by the WASI Preview 2 / Component-Model component.

The successor to :class:`rustfava.rustledger.engine.RustledgerEngine` (which
spawns the ``wasmtime`` CLI with JSON-RPC over stdin/stdout). This driver loads
``rustledger-ffi-component`` (rustledger #1384) once, in-process, via
``wasmtime-py``'s component API and calls its **typed** exports directly — no
subprocess per call, no hand-mirrored JSON DTOs.

This is the **default** engine (see ``rustfava.rustledger.get_engine``);
``RUSTFAVA_RUSTLEDGER_BACKEND=jsonrpc`` opts back into the legacy JSON-RPC
engine.

Results are marshalled from the component's typed `Record`/`Variant`/`list`
values into plain Python by a generic, *type-driven* converter
(:func:`_marshal`) that walks the component's own type metadata
(`RecordType.fields`, `VariantType.cases`), so no per-type field lists are
hand-maintained. Variants render as ``{"type": <case>, ...}`` (discriminated),
mirroring the JSON-RPC surface's tagged unions.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import urllib.request
from decimal import Decimal
from pathlib import Path
from typing import Any

from wasmtime import DirPerms
from wasmtime import Engine
from wasmtime import FilePerms
from wasmtime import Store
from wasmtime import WasiConfig
from wasmtime.component import Bool
from wasmtime.component import Component
from wasmtime.component import Linker
from wasmtime.component import ListType
from wasmtime.component import OptionType
from wasmtime.component import Record
from wasmtime.component import RecordType
from wasmtime.component import ResultType
from wasmtime.component import String
from wasmtime.component import TupleType
from wasmtime.component import Variant
from wasmtime.component import VariantType

from rustfava.rustledger.engine import _check_api_version
from rustfava.rustledger.engine import RUSTLEDGER_VERSION
from rustfava.rustledger.engine import RustledgerError

# The WIT interfaces of package ``rustledger:ledger``. This version string is
# used two ways: to build the interface IDs passed to ``get_export_index``, and
# to name the ``host`` instance registered on the linker below.
#
# Matching is by MAJOR, not by exact version. Measured against the pinned
# v0.21.0 component, which exports ``@3.4.0``:
#
#     pin 3.0.0 / 3.3.0 / 3.4.0 / 3.5.0 / 3.11.0
#         -> instantiates, version() = 3.4
#     pin 2.4.0 / 4.0.0
#         -> WasmtimeError
#
# Either direction works within a major; only a different major fails. Note
# where it fails — at instantiation, on the IMPORT side ("component imports
# instance ``rustledger:ledger/host@3.4.0``, but a match ..."), because
# ``_HOST`` below names the instance the linker offers -- not on export
# lookup, which is where the old note pointed.
#
# So a MINOR bump does not require touching this, and the previous note here —
# that a mismatch "makes ``get_export_index`` return ``None`` and every call
# fail" — was wrong: this file has been pinned to 3.3.0 against a 3.4.0
# component for as long as v0.21.0 has been pinned, and works.
#
# What a bump can genuinely break is a new MANDATORY IMPORT, which no version
# string reveals: WIT 3.1 -> 3.2 added ``host.decrypt`` and made the component
# un-instantiable until the linker grew the binding (the #218 incident).
# ``update-rustledger.yml`` therefore holds ANY WIT change for human review,
# and the question to answer is "what does the component import that
# ``_define_host_interface`` does not define" — inspect it with
# ``wasm-tools component wit``, not by comparing this constant.
#
# Kept in step with the pinned release anyway, as documentation of what the
# bindings were written against.
_WIT_VERSION = "3.4.0"
_LEDGER = f"rustledger:ledger/ledger@{_WIT_VERSION}"
_BUILDER = f"rustledger:ledger/builder@{_WIT_VERSION}"
_UTIL = f"rustledger:ledger/util@{_WIT_VERSION}"
_FORMAT = f"rustledger:ledger/format@{_WIT_VERSION}"


_COMPONENT_WASM_URL = (
    "https://github.com/rustledger/rustledger/releases/download/"
    f"{RUSTLEDGER_VERSION}/rustledger-ffi-component-{RUSTLEDGER_VERSION}.wasm"
)


# -- host capability: GPG decryption (WIT 3.2.0, rustledger#1667) -------------
#
# A WASI guest can neither spawn ``gpg`` nor reach the user's keyring, so the
# component imports ``rustledger:ledger/host@<wit>`` with a single
# ``decrypt: func(ciphertext: list<u8>) -> result<string, string>`` and calls
# it when it detects an encrypted (``.gpg``/``.asc``) input. The host runs the
# system ``gpg --batch --decrypt`` (keyring + gpg-agent for passphrases),
# matching rustledger's native loader semantics.
_HOST = f"rustledger:ledger/host@{_WIT_VERSION}"


def _host_decrypt(_store: Any, ciphertext: Any) -> Variant:
    try:
        proc = subprocess.run(
            ["gpg", "--batch", "--decrypt"],  # noqa: S607
            input=bytes(ciphertext),
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        return Variant(tag="err", payload=f"failed to run gpg: {exc}")
    if proc.returncode != 0:
        return Variant(
            tag="err",
            payload=proc.stderr.decode("utf-8", "replace").strip()
            or f"gpg exited with status {proc.returncode}",
        )
    try:
        return Variant(tag="ok", payload=proc.stdout.decode("utf-8"))
    except UnicodeDecodeError as exc:
        return Variant(
            tag="err", payload=f"decrypted content is not valid UTF-8: {exc}"
        )


def _define_host_interface(linker: Linker) -> None:
    """Register the ``host`` interface the component imports (WIT >= 3.2.0)."""
    with linker.root() as root, root.add_instance(_HOST) as host:
        host.add_func("decrypt", _host_decrypt)


def _default_wasm_path() -> Path:
    """Return the component wasm location (env override, else the cache path).

    Does not download — that happens lazily in ``RustledgerComponentEngine``
    so existence checks (e.g. test gating) stay side-effect free.
    """
    override = os.environ.get("RUSTLEDGER_COMPONENT_WASM")
    if override:
        return Path(override)
    return Path(__file__).parent / "rustledger_ffi_component.wasm"


def _download_component_wasm(wasm_path: Path) -> None:
    """Download the released component wasm to ``wasm_path``, best-effort.

    The artifact (``rustledger-ffi-component-<version>.wasm``) is attached to
    the rustledger GitHub release matching :data:`RUSTLEDGER_VERSION`. Releases
    that predate the component artifact return 404; on any failure this logs
    and leaves no file behind, so the caller surfaces a clear build-from-source
    error instead of a cryptic one.
    """
    print(  # noqa: T201
        f"Downloading rustledger component wasm ({RUSTLEDGER_VERSION})...",
        file=sys.stderr,
    )
    try:
        wasm_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(_COMPONENT_WASM_URL, wasm_path)  # noqa: S310
        print("Done.", file=sys.stderr)  # noqa: T201
    except Exception as e:  # noqa: BLE001
        wasm_path.unlink(missing_ok=True)
        print(  # noqa: T201
            f"Could not download component wasm: {e}",
            file=sys.stderr,
        )


def _snake(name: str) -> str:
    """WIT identifiers are kebab-case; the JSON-RPC surface is snake_case."""
    return name.replace("-", "_")


def _is_pair_list(vtype: Any) -> bool:
    """Whether ``vtype`` is ``list<tuple<_, _>>`` (WIT's string-keyed map)."""
    return (
        isinstance(vtype, ListType)
        and isinstance(vtype.element, TupleType)
        and len(vtype.element.elements) == 2
    )


def _pair_value_type(vtype: Any) -> Any:
    """The value type ``V`` of a ``list<tuple<string, V>>`` (a WIT map)."""
    return vtype.element.elements[1]


_META_VALUE_CASES = frozenset({"text", "number", "boolean", "amount", "null"})


def _is_meta_value(vtype: Any) -> bool:
    """Whether ``vtype`` is the WIT ``meta-value`` variant."""
    return isinstance(vtype, VariantType) and (
        frozenset(name for name, _ in vtype.cases) == _META_VALUE_CASES
    )


def _unwrap_query_value(cell: Any) -> Any:  # noqa: PLR0911
    """Project a marshalled query cell to the JSON-RPC ``value_to_json`` shape.

    ``RLCursor`` / the API serializer read that shape. The generic marshaller
    renders each cell as ``{"type": <case>, ...}``; rustledger's
    ``value_to_json`` instead emits bare values (text/bool/int as scalars,
    ``number`` as ``{number}``, ``inventory`` as ``{positions: [...]}``, etc.).
    Mirror it so query rows are consumable downstream.
    """
    if not isinstance(cell, dict) or "type" not in cell:
        return cell
    kind = cell["type"]
    if kind == "null":
        return None
    if kind in {"boolean", "integer", "text", "date", "string_set"}:
        return cell["value"]
    if kind == "number":
        return {"number": cell["value"]}
    if kind == "amount":
        return {"number": cell["number"], "currency": cell["currency"]}
    if kind == "inventory":
        return {"positions": [_drop_none(p) for p in cell["value"]]}
    if kind == "position":
        return _drop_none({k: v for k, v in cell.items() if k != "type"})
    if kind == "json":
        return json.loads(cell["value"])
    # interval / metadata: drop the discriminator, keep the fields.
    return {k: v for k, v in cell.items() if k != "type"}


def _drop_none(obj: Any) -> Any:
    """Drop ``None``-valued keys and sort keys to match ``value_to_json``.

    ``value_to_json`` omits absent ``cost``/``date``/``label`` (rather than
    emitting ``None``), and serde serializes maps alphabetically (``BTreeMap``)
    — so a position cell stringifies as ``{currency, number}``. Mirror both so
    object cells render identically to the JSON-RPC surface.
    """
    if isinstance(obj, dict):
        return {
            k: _drop_none(v) for k, v in sorted(obj.items()) if v is not None
        }
    if isinstance(obj, list):
        return [_drop_none(v) for v in obj]
    return obj


def _finalize_query_result(result: dict[str, Any]) -> dict[str, Any]:
    """Unwrap every query-value cell in a query result's rows in place."""
    rows = result.get("rows")
    if isinstance(rows, list):
        result["rows"] = [
            [_unwrap_query_value(cell) for cell in row] for row in rows
        ]
    return result


# The WIT ``cost-number`` variant. Since v0.20 (WIT 3.3) rustledger's JSON
# surface tags it by ``type`` with a ``value`` payload like every other
# variant (``per-unit-from-total`` carries a two-string list); v0.19 tagged
# it by ``kind`` and spread ``per_unit``/``total`` as fields, and the
# JSON-RPC layer sent a flat per-unit string — ``_cost_number_from_json``
# accepts all three so replayed entry JSON keeps loading. WIT 3.3 also added
# a ``compound`` input case, so detection is a superset check.
_COST_NUMBER_CASES = frozenset({"per-unit", "total", "per-unit-from-total"})


def _is_cost_number(vtype: Any) -> bool:
    """Whether ``vtype`` is the WIT ``cost-number`` variant."""
    return isinstance(vtype, VariantType) and (
        frozenset(name for name, _ in vtype.cases) >= _COST_NUMBER_CASES
    )


def _cost_number_to_json(value: Any, vtype: Any) -> dict[str, Any]:
    """Marshal a ``cost-number`` to the v0.20 ``type``-tagged JSON shape."""
    # NB: _marshal lowers WIT tuples to lists, so the pair case needs no
    # special handling here.
    payload = _marshal(value.payload, dict(vtype.cases)[value.tag])
    return {"type": _snake(value.tag), "value": payload}


def _is_typed_value(vtype: Any) -> bool:
    """Whether ``vtype`` is the WIT ``typed-value`` record (custom args)."""
    return isinstance(vtype, RecordType) and (
        frozenset(name for name, _ in vtype.fields)
        == frozenset({"value-type", "value"})
    )


def _typed_value_to_json(value: Any, vtype: Any) -> dict[str, Any]:
    """Marshal a ``typed-value`` to the JSON-RPC ``{type, value}`` shape.

    rustledger's ``TypedValue`` serializes the ``value-type`` field as ``type``
    and carries the bare value (amount as ``{number, currency}``), which Fava's
    ``RLCustomValue.from_raw`` reads. The generic record marshalling would emit
    ``{value_type, value: {type: ...}}`` instead.
    """
    fields = dict(vtype.fields)
    value_type = _marshal(getattr(value, "value-type"), fields["value-type"])
    payload = _marshal(value.value, fields["value"])
    return {"type": value_type, "value": _unwrap_meta_value(payload)}


def _typed_value_from_json(value: Any, vtype: Any) -> Any:
    """Rebuild a ``typed-value`` Record from the ``{type, value}`` shape.

    The inverse of :func:`_typed_value_to_json`, for clamp/filter inputs whose
    ``custom`` directives carry typed argument values.
    """
    vt = value.get("type", "string")
    payload = value.get("value")
    if vt == "amount" and isinstance(payload, dict):
        mv: dict[str, Any] = {
            "type": "amount",
            "number": str(payload.get("number")),
            "currency": payload.get("currency"),
        }
    elif vt == "number":
        mv = {"type": "number", "value": str(payload)}
    elif vt == "bool":
        mv = {"type": "boolean", "value": bool(payload)}
    elif vt == "null" or payload is None:
        mv = {"type": "null"}
    else:  # string/account/currency/tag/link/date all collapse to text
        mv = {"type": "text", "value": str(payload)}
    rec: Any = Record()
    setattr(rec, "value-type", str(vt))
    rec.value = _unmarshal(mv, dict(vtype.fields)["value"])
    return rec


def _cost_number_from_json(value: Any) -> Any:
    """Rebuild a ``cost-number`` Variant from the JSON-RPC / `types.py` shape.

    Accepts what the real caller passes: ``_cost_to_json`` emits a flat
    per-unit string, while component-marshalled input carries the
    ``kind``-tagged dict.
    """
    if isinstance(value, dict):
        kind = value.get("kind") or value.get("type")
        tag = _kebab(str(kind))
        payload = value.get("value")
        if tag == "per-unit-from-total":
            if isinstance(payload, (list, tuple)):  # v0.20 pair-as-list
                return Variant(tag, (str(payload[0]), str(payload[1])))
            # v0.19 spread the pair as per_unit/total fields
            return Variant(tag, (str(value["per_unit"]), str(value["total"])))
        if tag == "compound" and isinstance(payload, (list, tuple)):
            # WIT 3.3 input case (rustledger#1700): `{a # b}` as written —
            # (per-unit, LUMP-total). Pre-booking surfaces only; booked
            # egress rewrites to per-unit-from-total (rustfava#234).
            return Variant(tag, (str(payload[0]), str(payload[1])))
        return Variant(tag, str(payload))
    # A bare scalar (``_cost_to_json``'s flat string) is a per-unit cost.
    return Variant("per-unit", str(value))


def _unwrap_meta_value(value: Any) -> Any:
    """Flatten a marshalled ``meta-value`` variant to its scalar/plain form.

    User metadata values are a ``meta-value`` variant (text/number/boolean/
    amount/...). The JSON-RPC surface emitted them as plain scalars (or, for
    amounts, a bare ``{number, currency}`` object), not discriminated unions —
    so unwrap to match. (Directive and query-cell variants stay tagged.)
    """
    if isinstance(value, dict) and "type" in value:
        if set(value) == {"type", "value"}:
            return value["value"]
        return {k: v for k, v in value.items() if k != "type"}
    return value


def _marshal(value: Any, vtype: Any) -> Any:  # noqa: PLR0911, PLR0912
    """Convert a component value into plain Python, driven by its WIT type.

    Output matches the JSON-RPC engine's shapes so the same downstream
    (``loader``/``types``/``options``) parses both backends identically:

    - `Record` -> ``dict`` with **snake_case** keys (WIT names are kebab-case).
      A ``user`` field (``meta``'s user-metadata map) is **flattened** into the
      parent, mirroring the JSON-RPC ``Meta``'s ``#[serde(flatten)]``.
    - `Variant` -> ``{"type": <snake case>, ...}`` (discriminated; record
      payloads spread, other payloads under ``"value"``, unit cases bare).
    - `list<tuple<string, V>>` -> ``dict`` (WIT has no map type; the JSON-RPC
      surface emitted these — ``display-precision``, ``meta.user``, … — as
      objects). Other lists -> ``list``.
    - `option`/`result`/`tuple` unwrap; `enum`/primitives pass through.
    """
    if isinstance(vtype, RecordType):
        if _is_typed_value(vtype):
            return _typed_value_to_json(value, vtype)
        out: dict[str, Any] = {}
        for name, ftype in vtype.fields:
            marshalled = _marshal(getattr(value, name), ftype)
            if name == "user" and isinstance(marshalled, dict):
                # `meta.user` carries arbitrary user metadata; the JSON-RPC
                # `Meta` flattened it into the meta object (scalar values), so
                # do the same.
                out.update(
                    {k: _unwrap_meta_value(v) for k, v in marshalled.items()}
                )
            else:
                out[_snake(name)] = marshalled
        return out
    if isinstance(vtype, VariantType):
        if _is_cost_number(vtype):
            return _cost_number_to_json(value, vtype)
        cases = dict(vtype.cases)
        tag = value.tag
        payload_type = cases.get(tag)
        out_tag = _snake(tag)
        if payload_type is None or value.payload is None:
            return {"type": out_tag}
        payload = _marshal(value.payload, payload_type)
        if isinstance(payload, dict):
            return {"type": out_tag, **payload}
        return {"type": out_tag, "value": payload}
    if isinstance(vtype, ListType):
        items = [_marshal(item, vtype.element) for item in value]
        if _is_pair_list(vtype) and all(
            isinstance(p, list) and len(p) == 2 and isinstance(p[0], str)
            for p in items
        ):
            # ``list<meta-entry>`` (e.g. posting metadata): unwrap the tagged
            # meta-value to a scalar, matching how ``meta.user`` is flattened,
            # so downstream reads a bare string/number not ``{"type": ...}``.
            if _is_meta_value(_pair_value_type(vtype)):
                return {p[0]: _unwrap_meta_value(p[1]) for p in items}
            return {p[0]: p[1] for p in items}
        return items
    if isinstance(vtype, OptionType):
        return None if value is None else _marshal(value, vtype.payload)
    if isinstance(vtype, TupleType):
        return [
            _marshal(v, t) for v, t in zip(value, vtype.elements, strict=False)
        ]
    if isinstance(vtype, ResultType):
        # `result<ok, err>` lifts to a Variant(tag="ok"|"err"); wasmtime-py
        # does NOT raise. Surface `err` as an exception, unwrap `ok`.
        if value.tag == "err":
            err = _marshal(value.payload, vtype.err) if vtype.err else None
            msg = str(err) if err is not None else "component error"
            raise RustledgerError(msg)
        return _marshal(value.payload, vtype.ok) if vtype.ok else None
    # Fallback: an un-typed Record/Variant, an enum (lifts to str), or a
    # primitive.
    if isinstance(value, Record):
        return {
            _snake(k): getattr(value, k)
            for k in dir(value)
            if not k.startswith("_")
        }
    if isinstance(value, Variant):
        return {"type": _snake(value.tag), "value": value.payload}
    return value


def _kebab(name: str) -> str:
    """Inverse of :func:`_snake`: snake_case (JSON-RPC) -> WIT kebab-case."""
    return name.replace("_", "-")


def _meta_value_json(value: Any) -> dict[str, Any]:
    """Re-tag an unwrapped user-metadata scalar as a ``meta-value`` variant.

    Inverse of :func:`_unwrap_meta_value`, mirroring rustledger's
    ``json_to_meta_value`` (``types/input.rs``) so the reconstruction matches
    what the JSON-RPC ``entry.clamp`` does on the Rust side: ``str`` -> text,
    ``bool`` -> boolean, ``int``/``float``/``Decimal`` -> number, ``None`` ->
    null, ``{number, currency}`` -> amount, anything else -> null.
    """
    if isinstance(value, bool):  # before int — bool is an int subclass
        return {"type": "boolean", "value": value}
    if isinstance(value, str):
        return {"type": "text", "value": value}
    if isinstance(value, (int, float, Decimal)):
        return {"type": "number", "value": str(value)}
    if (
        isinstance(value, dict)
        and value.get("number") is not None
        and value.get("currency") is not None
    ):
        return {
            "type": "amount",
            "number": str(value["number"]),
            "currency": value["currency"],
        }
    return {"type": "null"}


def _default_for(vtype: Any) -> Any:
    """A benign default for a record field absent from the input dict.

    ``directives_to_json`` omits fields the loader fills in (e.g. the meta
    hash); the JSON-RPC engine relies on serde defaults, so we must supply
    type-appropriate zero values rather than ``None`` (which wasmtime rejects).
    """
    if isinstance(vtype, OptionType):
        return None
    if isinstance(vtype, ListType):
        return []
    if isinstance(vtype, RecordType):
        return _unmarshal({}, vtype)
    if isinstance(vtype, String):
        return ""
    if isinstance(vtype, Bool):
        return False
    # Remaining scalars are numeric (u32 lineno, s64, floats).
    return 0


def _unmarshal(value: Any, vtype: Any) -> Any:  # noqa: PLR0911, PLR0912
    """Convert plain Python into a typed component value (inverse of _marshal).

    Takes a value in :func:`_marshal`'s output shape and rebuilds the typed
    component value of type ``vtype``.
    Used for builder inputs: ``filter``/``clamp`` take ``list<directive>``, the
    same type ``load`` returns, so the entries Fava already holds round-trip
    back into the component. Records become :class:`wasmtime.component.Record`
    (fields set by their WIT name); tagged dicts become
    :class:`wasmtime.component.Variant`; the flattened ``meta.user`` keys are
    re-nested and re-tagged via :func:`_meta_value_json`.
    """
    if isinstance(vtype, RecordType):
        if _is_typed_value(vtype):
            return _typed_value_from_json(value, vtype)
        rec = Record()
        src = value if isinstance(value, dict) else {}
        non_user = {_snake(n) for n, _ in vtype.fields if n != "user"}
        for name, ftype in vtype.fields:
            if name == "user":
                # The keys `_marshal` flattened in (everything that isn't a
                # known `meta` field): re-nest as user metadata entries.
                mv_type = _pair_value_type(ftype)
                setattr(
                    rec,
                    name,
                    [
                        (k, _unmarshal(_meta_value_json(v), mv_type))
                        for k, v in src.items()
                        if k not in non_user
                    ],
                )
                continue
            key = _snake(name)
            setattr(
                rec,
                name,
                _unmarshal(src[key], ftype)
                if key in src
                else _default_for(ftype),
            )
        return rec
    if isinstance(vtype, VariantType):
        if _is_cost_number(vtype):
            return _cost_number_from_json(value)
        cases = dict(vtype.cases)
        tag = _kebab(value["type"])
        if tag not in cases:  # tolerate an already-kebab tag
            tag = value["type"]
        payload_type = cases[tag]
        if payload_type is None:
            return Variant(tag)
        if isinstance(payload_type, RecordType):
            payload = {k: v for k, v in value.items() if k != "type"}
            return Variant(tag, _unmarshal(payload, payload_type))
        return Variant(tag, _unmarshal(value["value"], payload_type))
    if isinstance(vtype, ListType):
        if _is_pair_list(vtype) and isinstance(value, dict):
            vt = _pair_value_type(vtype)
            # ``list<meta-entry>`` values arrive unwrapped (see `_marshal`);
            # re-tag as meta-value variants, mirroring the ``meta.user`` path.
            if _is_meta_value(vt):
                return [
                    (k, _unmarshal(_meta_value_json(v), vt))
                    for k, v in value.items()
                ]
            return [(k, _unmarshal(v, vt)) for k, v in value.items()]
        return [_unmarshal(item, vtype.element) for item in value]
    if isinstance(vtype, OptionType):
        return None if value is None else _unmarshal(value, vtype.payload)
    if isinstance(vtype, TupleType):
        return tuple(
            _unmarshal(v, t)
            for v, t in zip(value, vtype.elements, strict=False)
        )
    return value


class RustledgerComponentEngine:
    """In-process driver for the typed rustledger wasip2 component."""

    def __init__(self, wasm_path: Path | None = None) -> None:
        self._wasm_path = wasm_path or _default_wasm_path()
        # Auto-download only the default cache location — never an explicit
        # path or an `RUSTLEDGER_COMPONENT_WASM` override (caller-managed).
        uses_default = wasm_path is None and not os.environ.get(
            "RUSTLEDGER_COMPONENT_WASM",
        )
        if uses_default and not self._wasm_path.exists():
            _download_component_wasm(self._wasm_path)
        if not self._wasm_path.exists():
            msg = (
                f"rustledger component wasm not found at {self._wasm_path} "
                "and could not be downloaded (the pinned release may predate "
                "the component artifact). Build it with: cargo build -p "
                "rustledger-ffi-component --target wasm32-wasip2 --release, "
                "or set RUSTLEDGER_COMPONENT_WASM to a local build."
            )
            raise RustledgerError(msg)
        self._engine = Engine()
        self._component = Component.from_file(
            self._engine,
            str(self._wasm_path),
        )
        # Shared instance for source-based calls (load/query/validate/...);
        # the component holds no cross-call state for these. ``load_full``
        # builds a fresh instance with a pre-opened dir.
        self._store, self._inst = self._instantiate()
        self._iface_cache: dict[str, Any] = {}
        self._version_checked = False
        # The shared store/instance is reused across source-based calls and
        # wasmtime's `Store` is not concurrency-safe; serialize access since
        # Fava serves requests on multiple threads. (`load_full` uses a fresh
        # per-call instance and needs no lock.)
        self._lock = threading.Lock()

    # -- instantiation -----------------------------------------------------

    def _instantiate(
        self,
        preopen: tuple[str, str] | None = None,
    ) -> tuple[Store, Any]:
        store = Store(self._engine)
        wasi = WasiConfig()
        wasi.inherit_stdout()
        wasi.inherit_stderr()
        if preopen is not None:
            host, guest = preopen
            wasi.preopen_dir(
                host,
                guest,
                DirPerms.READ_ONLY,
                FilePerms.READ_ONLY,
            )
        store.set_wasi(wasi)
        linker = Linker(self._engine)
        linker.add_wasip2()
        _define_host_interface(linker)
        inst = linker.instantiate(store, self._component)
        return store, inst

    def _iface(self, name: str) -> Any:
        idx = self._iface_cache.get(name)
        if idx is None:
            idx = self._component.get_export_index(name)
            self._iface_cache[name] = idx
        return idx

    # -- typed calls -------------------------------------------------------

    def _call(self, iface: str, func_name: str, args: list[Any]) -> Any:
        """Call ``iface.func_name(*args)`` on the shared instance (locked)."""
        with self._lock:
            return self._call_on(
                self._store, self._inst, iface, func_name, args
            )

    def _call_on(
        self,
        store: Store,
        inst: Any,
        iface: str,
        func_name: str,
        args: list[Any],
    ) -> Any:
        """Call a func on a specific store/instance, marshalling the result."""
        fidx = self._component.get_export_index(func_name, self._iface(iface))
        func = inst.get_func(store, fidx)
        raw = func(store, *args)
        return _marshal(raw, func.type(store).result)

    def _ensure_version(self) -> None:
        if self._version_checked:
            return
        _check_api_version(self._call(_LEDGER, "version", []))
        self._version_checked = True

    # -- public API (mirrors RustledgerEngine) -----------------------------

    def version(self) -> str:
        """Return the component's ``api_version`` string (e.g. ``"3.2"``)."""
        return self._call(_LEDGER, "version", [])

    def load(
        self,
        source: str,
        filename: str = "<stdin>",
        *,
        expand_pads: bool = False,
    ) -> dict[str, Any]:
        """Parse + book ``source``; returns entries/errors/options/....

        ``filename`` is the directives' source location. When ``expand_pads``
        is true the engine materializes ``pad`` directives into synthesized
        ``Padding`` transactions (sorted by date, no source location) so
        balance-computing consumers see padded balances; the default keeps the
        source-faithful stream (rustledger #1628 / rustfava #192).
        """
        self._ensure_version()
        return self._call(_LEDGER, "load", [source, filename, expand_pads])

    def query(self, source: str, query_string: str) -> dict[str, Any]:
        """Run a BQL query over ``source``; returns columns/rows/errors."""
        self._ensure_version()
        return _finalize_query_result(
            self._call(_LEDGER, "query", [source, query_string])
        )

    def validate(self, source: str) -> dict[str, Any]:
        """Validate ``source``; returns ``valid`` + ``errors``."""
        self._ensure_version()
        return self._call(_LEDGER, "validate", [source])

    def format_entries(self, source: str) -> str:
        """Canonically reformat beancount ``source``."""
        self._ensure_version()
        return self._call(_FORMAT, "format-source", [source])

    def get_account_type(self, account: str) -> str:
        """Return the lowercased root type of ``account`` (or ``unknown``)."""
        return self._call(_UTIL, "get-account-type", [account])

    def is_encrypted(self, filepath: str) -> bool:
        """Return whether ``filepath`` looks like a ``.gpg``/``.asc`` file."""
        return self._call(_UTIL, "is-encrypted", [filepath])

    def load_full(
        self,
        path: str,
        *,
        allow_unrestricted_includes: bool = False,
        plugins: list[str] | None = None,
        expand_pads: bool = False,
    ) -> dict[str, Any]:
        """Load a file (resolving includes/plugins) via the component.

        When ``expand_pads`` is true the engine materializes ``pad`` directives
        into synthesized ``Padding`` transactions so balance-computing
        consumers see padded balances; the default keeps the source-faithful
        stream (rustledger #1628 / rustfava #192).

        Unlike the source-based calls this needs filesystem access, so it runs
        on a fresh instance with the file's directory pre-opened into the WASI
        sandbox at ``/work`` and the path rewritten accordingly.

        Note: only the entry file's own directory tree is granted to the WASI
        sandbox, so ``include`` targets must live at or below it — cross-tree
        (``../``) includes are unreachable here regardless of
        ``allow_unrestricted_includes`` (WASI denies the access before the
        loader's path-security check applies). A wider pre-open root would be
        needed to support them.
        """
        self._ensure_version()
        host_path = Path(path).resolve()
        guest_path = f"/work/{host_path.name}"
        store, inst = self._instantiate(
            preopen=(str(host_path.parent), "/work"),
        )
        result = self._call_on(
            store,
            inst,
            _LEDGER,
            "load-file",
            [
                guest_path,
                allow_unrestricted_includes,
                plugins or [],
                expand_pads,
            ],
        )
        # The component sees files under the WASI pre-open mount (``/work``),
        # so the directives it returns carry guest paths in ``meta.filename``
        # (and the include list). Map them back to real host paths — Fava opens
        # these files for editing, so a ``/work/...`` path would not exist.
        self._rewrite_guest_paths(result, host_path.parent)
        return result

    @staticmethod
    def _rewrite_guest_paths(result: dict[str, Any], host_dir: Path) -> None:
        """Rewrite ``/work/...`` guest paths in a load result to host paths."""

        def to_host(p: Any) -> Any:
            if isinstance(p, str) and p.startswith("/work/"):
                return str(host_dir / p[len("/work/") :])
            return p

        for entry in result.get("entries", []):
            meta = entry.get("meta")
            if isinstance(meta, dict) and "filename" in meta:
                meta["filename"] = to_host(meta["filename"])
        for include in result.get("includes", []):
            if isinstance(include, dict) and "path" in include:
                include["path"] = to_host(include["path"])

    def clamp_entries(
        self,
        entries_json: list[dict[str, Any]],
        begin_date: str,
        end_date: str,
    ) -> dict[str, Any]:
        """Clamp already-loaded entries to ``[begin, end)``.

        Mirrors :meth:`RustledgerEngine.clamp_entries`: synthesizes
        opening-balance and summary directives at the window boundaries. The
        entries are the same ``directive`` shape ``load`` emits, so they are
        marshalled back into typed component values via :func:`_unmarshal`
        before the call (the JSON-RPC engine instead ships the JSON and lets
        the Rust side reconstruct — same result, different layer).
        """
        return {
            "entries": self._builder_window(
                "clamp", entries_json, begin_date, end_date
            ),
        }

    def _builder_window(
        self,
        func_name: str,
        entries_json: list[dict[str, Any]],
        begin_date: str,
        end_date: str,
    ) -> list[dict[str, Any]]:
        """Run a ``builder`` window op (``filter``/``clamp``) on entries.

        Custom input marshalling means this can't reuse :meth:`_call`; it holds
        the shared-store lock around the whole call (typed in, marshalled out).
        """
        self._ensure_version()
        with self._lock:
            fidx = self._component.get_export_index(
                func_name, self._iface(_BUILDER)
            )
            func = self._inst.get_func(self._store, fidx)
            entries_type = func.type(self._store).params[0][1]
            wit_entries = _unmarshal(list(entries_json), entries_type)
            raw = func(self._store, wit_entries, begin_date, end_date)
            return _marshal(raw, func.type(self._store).result)

    def query_entries(
        self,
        entries_json: list[dict[str, Any]],
        query_string: str,
    ) -> dict[str, Any]:
        """Run a BQL query against already-loaded entries (no source re-parse).

        Marshals the entries into typed component values and calls the
        builder's ``query-entries`` — the typed alternative to re-rendering a
        filtered entry set back to beancount source text (which can render
        invalid text). Same ``columns``/``rows``/``errors`` shape as
        :meth:`query`.
        """
        self._ensure_version()
        with self._lock:
            fidx = self._component.get_export_index(
                "query-entries", self._iface(_BUILDER)
            )
            func = self._inst.get_func(self._store, fidx)
            entries_type = func.type(self._store).params[0][1]
            wit_entries = _unmarshal(list(entries_json), entries_type)
            raw = func(self._store, wit_entries, query_string)
            return _finalize_query_result(
                _marshal(raw, func.type(self._store).result)
            )

    # -- stateful ledger handle (WIT `resource session`, rustfava #173) -----

    def open_session(self, source: str) -> ComponentSession:
        """Load + book ``source`` into a held ledger session.

        The returned :class:`ComponentSession` keeps the booked ledger inside
        the component; its ``query``/``filter``/``clamp`` run server-side with
        no re-parse and no directive round-trip.
        """
        self._ensure_version()
        store, inst = self._instantiate()
        fidx = self._component.get_export_index(
            "[constructor]session", self._iface(_LEDGER)
        )
        handle = inst.get_func(store, fidx)(store, source)
        return ComponentSession(self, store, inst, handle)

    def open_session_entries(
        self, entries_json: list[dict[str, Any]]
    ) -> ComponentSession:
        """Hold an already-loaded entry set in a session (WIT >= 3.4.0).

        The entries marshal across the wire ONCE here; subsequent
        ``session.query`` calls run against directives held inside the
        component with no per-call shuttling — the missing piece that lets
        fava's FILTERED entry sets (#249) use sessions at all. Raises on
        components older than 3.4.0 (no ``from-entries`` export); callers
        gate/fall back (see ``rustfava.rustledger.query.SessionCache``).
        """
        self._ensure_version()
        store, inst = self._instantiate()
        fidx = self._component.get_export_index(
            "[static]session.from-entries", self._iface(_LEDGER)
        )
        func = inst.get_func(store, fidx)
        entries_type = func.type(store).params[0][1]
        wit_entries = _unmarshal(list(entries_json), entries_type)
        handle = func(store, wit_entries)
        return ComponentSession(self, store, inst, handle)

    def open_session_file(
        self,
        path: str,
        *,
        allow_unrestricted_includes: bool = False,
        plugins: list[str] | None = None,
    ) -> ComponentSession:
        """Like :meth:`open_session`, but load from a file path.

        Runs on a dedicated instance with the file's directory pre-opened into
        the WASI sandbox (matching :meth:`load_full`); the session maps the
        ``/work`` guest paths back to host paths in ``info()``.
        """
        self._ensure_version()
        host_path = Path(path).resolve()
        store, inst = self._instantiate(
            preopen=(str(host_path.parent), "/work"),
        )
        fidx = self._component.get_export_index(
            "[static]session.from-file", self._iface(_LEDGER)
        )
        handle = inst.get_func(store, fidx)(
            store,
            f"/work/{host_path.name}",
            allow_unrestricted_includes,
            plugins or [],
        )
        return ComponentSession(self, store, inst, handle, host_path.parent)


class ComponentSession:
    """A loaded, booked ledger held inside the component (WIT ``session``).

    Created by :meth:`RustledgerComponentEngine.open_session` /
    :meth:`~RustledgerComponentEngine.open_session_file`. ``query``/``filter``/
    ``clamp`` run against the held ledger server-side — no re-parse of source,
    no directive list shuttled across the FFI. Each session owns its own
    wasmtime store/instance (the resource handle is bound to them), so a file
    session can keep its WASI pre-open and sessions don't contend on one store.
    """

    def __init__(
        self,
        engine: RustledgerComponentEngine,
        store: Store,
        inst: Any,
        handle: Any,
        host_dir: Path | None = None,
    ) -> None:
        self._engine = engine
        self._store = store
        self._inst = inst
        self._handle = handle
        self._host_dir = host_dir
        self._lock = threading.Lock()

    def _method(self, name: str, *args: Any) -> Any:
        idx = self._engine._component.get_export_index(  # noqa: SLF001
            name,
            self._engine._iface(_LEDGER),  # noqa: SLF001
        )
        with self._lock:
            func = self._inst.get_func(self._store, idx)
            raw = func(self._store, self._handle, *args)
            return _marshal(raw, func.type(self._store).result)

    def info(self) -> dict[str, Any]:
        """The load result (entries/errors/options/plugins/includes)."""
        result: dict[str, Any] = self._method("[method]session.info")
        if self._host_dir is not None:
            RustledgerComponentEngine._rewrite_guest_paths(  # noqa: SLF001
                result, self._host_dir
            )
        return result

    def query(self, query_string: str) -> dict[str, Any]:
        """Run a BQL query against the held ledger."""
        return _finalize_query_result(
            self._method("[method]session.query", query_string)
        )

    def filter(self, begin_date: str, end_date: str) -> list[dict[str, Any]]:
        """Keep only directives within ``[begin, end)``."""
        return self._method("[method]session.filter", begin_date, end_date)

    def clamp(self, begin_date: str, end_date: str) -> list[dict[str, Any]]:
        """Clamp to ``[begin, end)`` with opening-balance synthesis."""
        return self._method("[method]session.clamp", begin_date, end_date)


_INSTANCE: RustledgerComponentEngine | None = None


def get_component_engine(
    wasm_path: Path | None = None,
) -> RustledgerComponentEngine:
    """Return the process-wide singleton component engine."""
    global _INSTANCE  # noqa: PLW0603
    if _INSTANCE is None:
        _INSTANCE = RustledgerComponentEngine(wasm_path)
    return _INSTANCE
