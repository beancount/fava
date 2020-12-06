"""
This is a PyInstaller hook needed to successfully freeze fava.
"""
from PyInstaller.utils.hooks import (
    collect_data_files,
)  # pylint: disable=import-error
from PyInstaller.utils.hooks import (
    copy_metadata,
)  # pylint: disable=import-error

datas = collect_data_files("fava")
datas += copy_metadata("fava")
