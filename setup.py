"""Setup script for Fava.

The configuration is in setup.cfg.
"""
import subprocess
from distutils.cmd import Command
from distutils.log import INFO

from setuptools import setup
from setuptools.command.build_py import build_py


class BuildFrontend(Command):
    """Custom command `setup.py build_frontend` to build fava's frontend."""

    def initialize_options(self) -> None:
        pass

    def finalize_options(self) -> None:
        pass

    def run(self) -> None:
        command = ["make"]
        self.announce(f"Running command {command}", level=INFO)
        subprocess.check_call(command)


class BuildPy(build_py):
    """Custom command `setup.py build` to build fava including its frontend."""

    def run(self):
        self.run_command("build_frontend")
        super().run()


setup(
    cmdclass={
        "build_frontend": BuildFrontend,
        "build_py": BuildPy,
    }
)
