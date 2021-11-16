from decompile_ng.scanner import get_scanner
from decompile_ng.parsers.main import get_python_parser


def test_get_scanner():
    # See that we can retrieve a scanner using a full version number
    assert get_scanner((3, 10, 0))


def test_get_parser():
    # See that we can retrieve a sparser using a full version number
    assert get_python_parser((3, 10, 0))
