# pylint: disable=missing-docstring
from pathlib import Path
from textwrap import dedent

from beancount.loader import load_file


def test_plugins(tmp_path: Path) -> None:
    # Create sample files
    assets_cash = tmp_path / "documents" / "Assets" / "Cash"
    assets_cash.mkdir(parents=True)
    discovered = "2016-11-05 Test 4 discovered.pdf"
    (assets_cash / discovered).touch()
    non_discovered = "Test 5.pdf"
    (assets_cash / non_discovered).touch()

    assets_cash_rel = Path("documents") / "Assets" / "Cash"

    beancount_file = tmp_path / "example-tag-discovered.beancount"
    beancount_file.write_text(
        dedent(
            f"""
        option "title" "Test tag discovered documents"
        option "operating_currency" "EUR"
        option "documents" "{tmp_path / "documents"}"

        plugin "fava.plugins.tag_discovered_documents"

        2016-10-31 open Assets:Cash

        2016-11-06 document Assets:Cash "{assets_cash_rel / non_discovered}"
        """.replace(
                "\\", "\\\\"
            )
        )
    )

    entries, errors, _ = load_file(str(beancount_file))

    assert not errors
    assert len(entries) == 3

    assert discovered in entries[1].filename
    assert "discovered" in entries[1].tags

    assert non_discovered in entries[2].filename
    assert not entries[2].tags
