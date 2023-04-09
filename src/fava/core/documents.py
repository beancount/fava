"""Document path related helpers."""
from __future__ import annotations

from os import altsep
from os import sep
from os.path import abspath
from os.path import dirname
from os.path import join
from os.path import normpath
from typing import TYPE_CHECKING

from fava.helpers import FavaAPIError

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger


def is_document_or_import_file(filename: str, ledger: FavaLedger) -> bool:
    """Check whether the filename is a document or in an import directory.

    Args:
        filename: The filename to check.
        ledger: The FavaLedger.

    Returns:
        Whether this is one of the documents or a path in an import dir.
    """
    filenames = [
        document.filename for document in ledger.all_entries_by_type.Document
    ]
    import_directories = [
        ledger.join_path(d) for d in ledger.fava_options.import_dirs
    ]
    if filename in filenames:
        return True
    file_path = abspath(filename)
    if any(file_path.startswith(d) for d in import_directories):
        return True
    return False


def filepath_in_document_folder(
    documents_folder: str, account: str, filename: str, ledger: FavaLedger
) -> str:
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
        raise FavaAPIError(f"Not a documents folder: {documents_folder}.")

    if account not in ledger.attributes.accounts:
        raise FavaAPIError(f"Not a valid account: '{account}'")

    for separator in sep, altsep:
        if separator:
            filename = filename.replace(separator, " ")

    return normpath(
        join(
            dirname(ledger.beancount_file_path),
            documents_folder,
            *account.split(":"),
            filename,
        )
    )
