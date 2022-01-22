from typing import Any

from fava.util.typing import LoaderResult

# class LoadError(NamedTuple):
#     source: Any
#     message: Any
#     entry: Any
#
# DEFAULT_PLUGINS_PRE: Any
# DEFAULT_PLUGINS_POST: Any
# RENAMED_MODULES: Any
# PICKLE_CACHE_FILENAME: str
# PICKLE_CACHE_THRESHOLD: float

def load_file(
    filename: str,
    log_timings: Any | None = ...,
    log_errors: Any | None = ...,
    extra_validations: Any | None = ...,
    encoding: Any | None = ...,
) -> LoaderResult: ...

# def load_encrypted_file(
#     filename,
#     log_timings: Any | None = ...,
#     log_errors: Any | None = ...,
#     extra_validations: Any | None = ...,
#     dedent: bool = ...,
#     encoding: Any | None = ...,
# ): ...
# def get_cache_filename(pattern: str, filename: str) -> str: ...
# def pickle_cache_function(cache_getter, time_threshold, function): ...
# def delete_cache_function(cache_getter, function): ...
# def needs_refresh(options_map): ...
# def compute_input_hash(filenames): ...
def load_string(
    string: str,
    log_timings: Any | None = ...,
    log_errors: Any | None = ...,
    extra_validations: Any | None = ...,
    dedent: bool = ...,
    encoding: Any | None = ...,
) -> LoaderResult: ...

# def aggregate_options_map(options_map, src_options_map) -> None: ...
# def run_transformations(entries, parse_errors, options_map, log_timings): ...
# def combine_plugins(*plugin_modules): ...
# def load_doc(expect_errors: bool = ...): ...
# def initialize(use_cache: bool, cache_filename: Optional[str] = ...): ...
