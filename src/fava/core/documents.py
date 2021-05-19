"""Document path related helpers."""
import os
from os import path
from typing import TYPE_CHECKING

from fava.helpers import FavaAPIException

if TYPE_CHECKING:
    from fava.core import FavaLedger


def is_document_or_import_file(filename: str, ledger: "FavaLedger") -> bool:
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
        ledger.join_path(d) for d in ledger.fava_options["import-dirs"]
    ]
    if filename in filenames:
        return True
    file_path = path.abspath(filename)
    if any(file_path.startswith(d) for d in import_directories):
        return True
    return False


def filepath_in_document_folder(
    documents_folder: str, account: str, filename: str, ledger: "FavaLedger"
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
        raise FavaAPIException(f"Not a documents folder: {documents_folder}.")

    if account not in ledger.attributes.accounts:
        raise FavaAPIException(f"Not a valid account: '{account}'")

    for sep in os.sep, os.altsep:
        if sep:
            filename = filename.replace(sep, " ")

    return path.normpath(
        path.join(
            path.dirname(ledger.beancount_file_path),
            documents_folder,
            *account.split(":"),
            filename,
        )
    )
