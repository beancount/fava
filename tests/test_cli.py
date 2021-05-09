# pylint: disable=missing-docstring
import os
import sys
from socket import socket
from subprocess import PIPE
from subprocess import Popen
from subprocess import STDOUT
from time import sleep
from time import time

import pytest

from .conftest import EXAMPLE_FILE

HOST = "0.0.0.0"
FAVA = ("fava",)

if "BEANCOUNT_FILE" in os.environ:
    del os.environ["BEANCOUNT_FILE"]


def get_port() -> int:
    sock = socket()
    sock.bind((HOST, 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def output_contains(process: Popen, output: str, timeout: int) -> bool:
    endtime = time() + timeout
    while True:
        if time() > endtime or not process.stdout:
            return False
        if output in process.stdout.readline():
            return True
        sleep(0.1)


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_cli() -> None:
    port = str(get_port())
    args = (EXAMPLE_FILE, "-d", "-p", port)
    with Popen(
        FAVA + args,
        stdout=PIPE,
        stderr=STDOUT,
        universal_newlines=True,
    ) as process:
        assert output_contains(process, "Running on", 20)
        with Popen(
            FAVA + args,
            stdout=PIPE,
            stderr=STDOUT,
            universal_newlines=True,
        ) as process2:
            process2.wait()
            process.terminate()
            assert process2.stdout
            assert "in use" in "".join(process2.stdout.readlines())
            assert process2.returncode == 2
