import os
import signal
import socket
import subprocess
import time

from .conftest import EXAMPLE_FILE

HOST = '0.0.0.0'
FAVA = ('fava',)

if 'BEANCOUNT_FILE' in os.environ:
    del os.environ['BEANCOUNT_FILE']


def _get_port():
    sock = socket.socket()
    sock.bind((HOST, 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def _wait_for_output(process, output, timeout):
    endtime = time.time() + timeout
    while True:
        if time.time() > endtime:
            return
        if output in process.stdout.readline():
            return
        time.sleep(.1)


def _run_fava(args=None):
    proc = FAVA + args if args else FAVA
    return subprocess.Popen(proc,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True)


def test_cli_basic():
    port = _get_port()
    args = (EXAMPLE_FILE, '-p', str(port))
    process = _run_fava(args)
    _wait_for_output(process, 'Running on', 20)
    process.send_signal(signal.SIGINT)
    process.wait()


def test_cli_prefix():
    args = (EXAMPLE_FILE, '-p', str(_get_port()), '--prefix', '/test')
    process = _run_fava(args)
    _wait_for_output(process, 'Running on', 20)
    process.send_signal(signal.SIGINT)
    process.wait()


def test_cli_empty():
    process = _run_fava()
    process.wait()
    assert 'No file specified' in ''.join(process.stdout.readlines())
    assert process.returncode == 2


def test_cli_addrinuse():
    args = (EXAMPLE_FILE, '-p', str(_get_port()))
    process = _run_fava(args)
    _wait_for_output(process, 'Running on', 20)
    process2 = _run_fava(args)
    process2.wait()
    process.send_signal(signal.SIGINT)
    assert 'in use' in ''.join(process2.stdout.readlines())
    assert process2.returncode == 2
