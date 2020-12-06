# pylint: skip-file
# mypy: ignore-errors
"""
This is a PyInstaller hook needed to successfully freeze fava.
"""
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata

datas = collect_data_files("fava")
datas += copy_metadata("fava")
