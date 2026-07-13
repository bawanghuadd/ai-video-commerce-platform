import pytest

from tests.conftest import validate_test_database_url


@pytest.mark.parametrize(
    "url",
    [
        "mysql+pymysql://user:password@localhost/production",
        "sqlite+pysqlite:///local.sqlite3",
    ],
)
def test_rejects_database_urls_without_test_marker(url):
    with pytest.raises(RuntimeError):
        validate_test_database_url(url)


def test_accepts_explicit_isolated_database_url():
    url = "mysql+pymysql://user:password@localhost/app_ci"
    assert validate_test_database_url(url) == url
