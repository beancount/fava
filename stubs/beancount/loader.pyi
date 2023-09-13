from typing import Any

from fava.beans.types import LoaderResult

def load_file(
    filename: str,
    log_timings: Any | None = ...,
    log_errors: Any | None = ...,
    extra_validations: Any | None = ...,
    encoding: Any | None = ...,
) -> LoaderResult: ...
def load_string(
    string: str,
    log_timings: Any | None = ...,
    log_errors: Any | None = ...,
    extra_validations: Any | None = ...,
    *,
    dedent: bool = ...,
    encoding: Any | None = ...,
) -> LoaderResult: ...
