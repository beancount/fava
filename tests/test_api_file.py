from textwrap import dedent
from fava.api.file import (next_key, leading_space, insert_metadata_in_file,
                           find_insert_marker, insert_transaction_in_file)


def test_next_key():
    assert next_key('statement', []) == 'statement'
    assert next_key('statement', ['foo']) == 'statement'
    assert next_key('statement', ['foo', 'statement']) == 'statement-2'
    assert next_key('statement', ['statement', 'statement-2']) == 'statement-3'


def test_leading_space():
    assert leading_space('test') == ''
    assert leading_space('	test') == '	'
    assert leading_space('  test') == '  '
    assert leading_space('    2016-10-31 * "Test" "Test"') == '    '
    assert leading_space('\r\t\r\ttest') == '\r\t\r\t'
    assert leading_space('\ntest') == '\n'


def test_insert_metadata_in_file(tmpdir):
    file_content = dedent("""
        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD
    """)
    samplefile = tmpdir.mkdir('fava_util_file').join('example.beancount')
    samplefile.write(file_content)

    assert samplefile.read() == dedent(file_content)
    assert len(tmpdir.listdir()) == 1

    insert_metadata_in_file(str(samplefile), 1, 'metadata', 'test1')
    assert samplefile.read() == dedent("""
        2016-02-26 * "Uncle Boons" "Eating out alone"
            metadata: "test1"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD
    """)

    insert_metadata_in_file(str(samplefile), 1, 'metadata', 'test2')
    assert samplefile.read() == dedent("""
        2016-02-26 * "Uncle Boons" "Eating out alone"
            metadata: "test2"
            metadata: "test1"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD
    """)


def test_find_insert_marker(tmpdir):
    file_content = dedent("""
        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD

        ; FAVA-INSERT-MARKER
        ; Hello World
    """)
    testdir = tmpdir.mkdir('fava_util_file2')
    samplefile = testdir.join('example2.beancount')
    samplefile.write(file_content)
    samplefile_nomarker = testdir.join('example3.beancount')
    samplefile_nomarker.write("Hello World!")

    assert samplefile.read() == dedent(file_content)
    assert len(tmpdir.listdir()) == 1

    filename, lineno = find_insert_marker([str(samplefile)])
    assert filename == str(samplefile)
    assert lineno == 5

    filename, lineno = find_insert_marker(
        [str(samplefile_nomarker), str(samplefile)])
    assert filename == str(samplefile)
    assert lineno == 5

    filename, lineno = find_insert_marker([str(samplefile_nomarker)])
    assert filename == str(samplefile_nomarker)
    assert lineno == 2


def test_insert_transaction_in_file(tmpdir):
    file_content = dedent("""
        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD
    """)
    samplefile = tmpdir.mkdir('fava_util_file3').join('example.beancount')
    samplefile.write(file_content)

    assert samplefile.read() == dedent(file_content)
    assert len(tmpdir.listdir()) == 1

    insert_transaction_in_file(str(samplefile), 1, 'Test\n')
    assert samplefile.read() == dedent("""
        Test

        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD
    """)
