import pytest
from flask import Flask
from flask_calendar.app_utils import task_details_for_markup
from markupsafe import Markup, escape

SOURCE_STRING_PLACEHOLDER = "pre {} post"
EXPECTED_STRING_PLACEHOLDER = 'pre <a href="{}" target="_blank">{}</a> post'


@pytest.mark.parametrize(
    "url, description",
    [
        ("http://test.test", "standard http url"),
        ("https://test.test", "standard https url"),
        ("http://www.test.test", "www-prefixed url"),
        ("http://127.0.0.1", "ip url"),
        ("http://test.test/?test=test&test2=test2", "url with query string"),
        ("http://test.test/?param1=value1&param2=value2", "url with ampersand"),
        ("http://test.test/?param1=value1&param2[]=value2", "url with brackets"),
        ("http://test.test/#some=thing", "url with hash"),
        ("http://test.test/#some~thing", "url with similarity symbol"),
        ("http://test.test/?test=A+B", "url with plus sign"),
    ],
)
def test_supported_task_details_for_markup(app: Flask, url: str, description: str) -> None:
    with app.app_context():
        expected = EXPECTED_STRING_PLACEHOLDER.format(escape(url), escape(url))
        actual = task_details_for_markup(SOURCE_STRING_PLACEHOLDER.format(url))
        assert expected == actual


@pytest.mark.parametrize(
    "url, description",
    [
        ("http://localhost/", "localhost url"),
        ("http://test.test:8000", "specified port url"),
        ("192.168.1.1", "numeric url without http(s)"),
        ("www.test.test", "url without http(s)"),
        ("ftp.test.test", "ftp url"),
    ],
)
def test_unsupported_task_details_for_markup(app: Flask, url: str, description: str) -> None:
    with app.app_context():
        expected = EXPECTED_STRING_PLACEHOLDER.format(url, url)
        actual = task_details_for_markup(SOURCE_STRING_PLACEHOLDER.format(url))
        assert expected != actual


@pytest.mark.parametrize(
    "details, expected",
    [
        ("<script>alert(1)</script>", "&lt;script&gt;alert(1)&lt;/script&gt;"),
        ("<img src=x onerror=alert(1)>", "&lt;img src=x onerror=alert(1)&gt;"),
        ('"><svg onload=1>', "&#34;&gt;&lt;svg onload=1&gt;"),
        ("line1<br>line2<script>", "line1<br>line2&lt;script&gt;"),
        ("a &amp; b", "a &amp;amp; b"),
        ("javascript:alert(1)", "javascript:alert(1)"),
        ("HTTP://x", "HTTP://x"),
    ],
    ids=[
        "script",
        "img-onerror",
        "attribute-breakout",
        "keeps-line-breaks",
        "no-double-unescape",
        "javascript",
        "uppercase",
    ],
)
def test_task_details_for_markup_escapes_html(app: Flask, details: str, expected: str) -> None:
    with app.app_context():
        assert expected == task_details_for_markup(details)


def test_task_details_for_markup_escapes_text_around_urls(app: Flask) -> None:
    with app.app_context():
        actual = task_details_for_markup("pre <b>x</b> http://test.test/?a=1&b=2 post")

        escaped_url = "http://test.test/?a=1&amp;b=2"
        expected = 'pre &lt;b&gt;x&lt;/b&gt; <a href="{0}" target="_blank">{0}</a> post'.format(escaped_url)
        assert expected == actual


@pytest.mark.parametrize("details", ["&nbsp;", ""])
def test_task_details_for_markup_keeps_empty_details_unchanged(app: Flask, details: str) -> None:
    with app.app_context():
        assert details == task_details_for_markup(details)


def test_task_details_for_markup_escapes_when_auto_decorate_is_disabled(app: Flask) -> None:
    app.config["AUTO_DECORATE_TASK_DETAILS_HYPERLINK"] = False

    with app.app_context():
        actual = task_details_for_markup("<script>x</script> http://test.test")

        assert "&lt;script&gt;x&lt;/script&gt; http://test.test" == actual


def test_task_details_for_markup_returns_markup(app: Flask) -> None:
    with app.app_context():
        assert isinstance(task_details_for_markup("text"), Markup)
