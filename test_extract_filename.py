import pytest

from download import extract_from_link_extension

@pytest.mark.parametrize(
    'raw_link, expected_value',
    (
        ("http://example.com/image.png#about_python", ".png"),
        ("http://example.com/image.jpg?v=9341124", ".jpg"),
        ("https://example.com/txt/hello%20world.txt?v=9#python", ".txt"),
        ("http://example.com/image.png", ".png"),
    ),
)
def test_parse_column(raw_link, expected_value):
    assert extract_from_link_extension(raw_link) == expected_value