"""Document path related helpers."""

from __future__ import annotations

from os import altsep
from os import sep
from pathlib import Path
from typing import TYPE_CHECKING

from rustfava.helpers import RustfavaAPIError

if TYPE_CHECKING:  # pragma: no cover
    from rustfava.core import RustfavaLedger


class NotADocumentsFolderError(RustfavaAPIError):
    """Not a documents folder."""

    def __init__(self, folder: str) -> None:
        super().__init__(f"Not a documents folder: {folder}.")


class NotAValidAccountError(RustfavaAPIError):
    """Not a valid account."""

    def __init__(self, account: str) -> None:
        super().__init__(f"Not a valid account: '{account}'")


def is_document_or_import_file(filename: str, ledger: RustfavaLedger) -> bool:
    """Check whether the filename is a document or in an import directory.

    This is a security validation function that prevents path traversal.

    Args:
        filename: The filename to check.
        ledger: The RustfavaLedger.

    Returns:
        Whether this is one of the documents or a path in an import dir.
    """
    # Check if it's an exact match for a known document
    if any(
        filename == d.filename for d in ledger.all_entries_by_type.Document
    ):
        return True
    # Check if resolved path is within an import directory (prevents path traversal)
    file_path = Path(filename).resolve()
    for import_dir in ledger.fava_options.import_dirs:
        resolved_dir = ledger.join_path(import_dir).resolve()
        if file_path.is_relative_to(resolved_dir):
            return True
    return False


def filepath_in_document_folder(
    documents_folder: str,
    account: str,
    filename: str,
    ledger: RustfavaLedger,
) -> Path:
    """File path for a document in the folder for an account.

    Args:
        documents_folder: The documents folder.
        account: The account to choose the subfolder for.
        filename: The filename of the document.
        ledger: The RustfavaLedger.

    Returns:
        The path that the document should be saved at.
    """
    if documents_folder not in ledger.options["documents"]:
        raise NotADocumentsFolderError(documents_folder)

    if account not in ledger.attributes.accounts:
        raise NotAValidAccountError(account)

    filename = filename.replace(sep, " ")
    if altsep:  # pragma: no cover
        filename = filename.replace(altsep, " ")

    return ledger.join_path(
        documents_folder,
        *account.split(":"),
        filename,
    )
