"""Document path related helpers."""

from __future__ import annotations

from os import altsep
from os import sep
from pathlib import Path
from typing import TYPE_CHECKING

from fava.helpers import FavaAPIError

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger


class NotADocumentsFolderError(FavaAPIError):
    """Not a documents folder."""

    def __init__(self, folder: str) -> None:
        super().__init__(f"Not a documents folder: {folder}.")


class NotAValidAccountError(FavaAPIError):
    """Not a valid account."""

    def __init__(self, account: str) -> None:
        super().__init__(f"Not a valid account: '{account}'")


def is_document_or_import_file(filename: str, ledger: FavaLedger) -> bool:
    """Check whether the filename is a document or in an import directory.

    Args:
        filename: The filename to check.
        ledger: The FavaLedger.

    Returns:
        Whether this is one of the documents or a path in an import dir.
    """
    if any(
        filename == d.filename for d in ledger.all_entries_by_type.Document
    ):
        return True
    file_path = Path(filename).resolve()
    return any(
        str(file_path).startswith(str(ledger.join_path(d)))
        for d in ledger.fava_options.import_dirs
    )


def filepath_in_document_folder(
    documents_folder: str,
    account: str,
    filename: str,
    ledger: FavaLedger,
) -> Path:
    """File path for a document in the folder for an account.

    Args:
        documents_folder: The documents folder.
        account: The account to choose the subfolder for.
        filename: The filename of the document.
        ledger: The FavaLedger.

    Returns:
        The path that the document should be saved at.
    """
    if documents_folder not in ledger.options["documents"]:
        raise NotADocumentsFolderError(documents_folder)

    if account not in ledger.attributes.accounts:
        raise NotAValidAccountError(account)

    for separator in sep, altsep:
        if separator:
            filename = filename.replace(separator, " ")

    return ledger.join_path(
        documents_folder,
        *account.split(":"),
        filename,
    )
