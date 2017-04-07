import pytest

from fava.core import FavaLedger


@pytest.fixture
def ingest_module(tmpdir):
    ingest_dirs = tmpdir.mkdir('downloads')
    ingest_config = tmpdir.mkdir('importers').join('ingest.config')
    ingest_config.write('CONFIG = []')

    bcontent = """
2017-01-01 custom "fava-option" "ingest-config" "{}"
2017-01-01 custom "fava-option" "ingest-dirs" "{}"
    """.format(ingest_config, ingest_dirs)
    bfile = tmpdir.join('example_ingest.beancount')
    bfile.write(bcontent)

    ingest = FavaLedger(bfile).ingest
    return ingest


def test_ingest_config(ingest_module):
    assert ingest_module.config is not None


def test_ingest_noconfig(example_ledger):
    assert example_ledger.ingest.config is None
