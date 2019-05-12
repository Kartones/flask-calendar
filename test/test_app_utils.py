from app_utils import task_details_for_markup


SOURCE_STRING_PLACEHOLDER = "pre {} post"
EXPECTED_STRING_PLACEHOLDER = "pre <a href=\"{}\" target=\"_blank\">{}</a> post"


def test_http_standard_url_is_supported() -> None:
    url = "http://test.test"
    expected = EXPECTED_STRING_PLACEHOLDER.format(url, url)
    actual = task_details_for_markup(SOURCE_STRING_PLACEHOLDER.format(url))

    assert expected == actual


def test_https_standard_url_is_supported() -> None:
    url = "https://test.test"
    expected = EXPECTED_STRING_PLACEHOLDER.format(url, url)
    actual = task_details_for_markup(SOURCE_STRING_PLACEHOLDER.format(url))

    assert expected == actual


def test_www_prefixed_url_is_supported() -> None:
    url = "http://www.test.test"
    expected = EXPECTED_STRING_PLACEHOLDER.format(url, url)
    actual = task_details_for_markup(SOURCE_STRING_PLACEHOLDER.format(url))

    assert expected == actual


def test_ip_url_is_supported() -> None:
    url = "http://127.0.0.1"
    expected = EXPECTED_STRING_PLACEHOLDER.format(url, url)
    actual = task_details_for_markup(SOURCE_STRING_PLACEHOLDER.format(url))

    assert expected == actual


def test_querystring_parameters_url_is_supported() -> None:
    url = "http://test.test/?test=test&test2=test2"
    expected = EXPECTED_STRING_PLACEHOLDER.format(url, url)
    actual = task_details_for_markup(SOURCE_STRING_PLACEHOLDER.format(url))

    assert expected == actual


# Unsupported urls


def test_hash_url_is_unsupported() -> None:
    url = "http://test.test/#some=thing"
    expected = EXPECTED_STRING_PLACEHOLDER.format(url, url)
    actual = task_details_for_markup(SOURCE_STRING_PLACEHOLDER.format(url))

    assert expected != actual


def test_localhost_url_is_unsupported() -> None:
    url = "http://localhost/"
    expected = EXPECTED_STRING_PLACEHOLDER.format(url, url)
    actual = task_details_for_markup(SOURCE_STRING_PLACEHOLDER.format(url))

    assert expected != actual


def test_specified_port_url_is_unsupported() -> None:
    url = "http://test.test:8000"
    expected = EXPECTED_STRING_PLACEHOLDER.format(url, url)
    actual = task_details_for_markup(SOURCE_STRING_PLACEHOLDER.format(url))

    assert expected != actual
