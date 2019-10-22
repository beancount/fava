"""Setup script for Fava.

The configuration is in setup.cfg.
"""
from platform import system
from importlib.machinery import EXTENSION_SUFFIXES
import os

from setuptools import Extension
from setuptools import setup
from setuptools.command.build_ext import build_ext


class BuildTreeSitter(build_ext):
    """Build a tree_sitter grammar."""

    def get_ext_filename(self, fullname):
        # Use simple file ending, since this extension doesn't depend on
        # Python.
        return os.path.join(*fullname.split(".")) + EXTENSION_SUFFIXES[-1]

    def get_export_symbols(self, ext):
        # On Windows, the existence of the PyINIT_x function is checked
        # otherwise. Since we're not building a Python extension but just a
        # library, that would fail.
        return None


FLAGS = None if system() == "Windows" else ["-std=c99"]

setup(
    cmdclass={"build_ext": BuildTreeSitter},
    ext_modules=[
        Extension(
            "fava.parser.tree_sitter_beancount",
            ["fava/parser/tree-sitter-beancount/parser.c"],
            include_dirs=["fava/parser/tree-sitter-beancount"],
            extra_compile_args=FLAGS,
        )
    ],
)
