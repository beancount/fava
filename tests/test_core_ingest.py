import pytest

from fava.core import FavaLedger


@pytest.fixture
def ingest_module(tmpdir):
    ingest_dirs = tmpdir.mkdir('downloads')
    ingest_config = tmpdir.mkdir('importers').join('ingest.config')
    ingest_config.write('CONFIG = ["test"]')

    bcontent = """
2017-01-01 custom "fava-option" "import-config" "{}"
2017-01-01 custom "fava-option" "import-dirs" "{}"
    """.format(ingest_config, ingest_dirs)
    bfile = tmpdir.join('example_ingest.beancount')
    bfile.write(bcontent)

    ingest = FavaLedger(bfile).ingest
    return ingest


def test_ingest_config(ingest_module):
    assert ingest_module.config


def test_ingest_noconfig(example_ledger):
    assert not example_ledger.ingest.config
