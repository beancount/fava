# pylint: disable=missing-docstring
import os
import socket
import subprocess
import sys
import time

import pytest

from .conftest import EXAMPLE_FILE

HOST = "0.0.0.0"
FAVA = ("fava",)

if "BEANCOUNT_FILE" in os.environ:
    del os.environ["BEANCOUNT_FILE"]


def get_port():
    sock = socket.socket()
    sock.bind((HOST, 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def output_contains(process, output, timeout):
    endtime = time.time() + timeout
    while True:
        if time.time() > endtime:
            return False
        if output in process.stdout.readline():
            return True
        time.sleep(0.1)


def run_fava(args=()):
    return subprocess.Popen(
        FAVA + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_cli():
    port = str(get_port())
    args = (EXAMPLE_FILE, "-d", "-p", port)
    process = run_fava(args)
    assert output_contains(process, "Running on", 20)
    process2 = run_fava(args)
    process2.wait()
    process.terminate()
    process.wait()
    assert "in use" in "".join(process2.stdout.readlines())
    assert process2.returncode == 2
