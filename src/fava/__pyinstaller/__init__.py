"""
This package provides a hook for PyInstaller to successfully freeze fava.
"""
import os


def get_hook_dirs():
    """This function is referenced in fava's package configuration."""
    return [os.path.dirname(__file__)]
