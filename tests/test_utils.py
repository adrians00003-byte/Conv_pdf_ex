import re
import pytest

from main_files.utils import money


def test_money_parses_valid_values():
    assert money("1,234.56") == 1234.56
    assert money("$1,234.56") == 1234.56
    assert money("$ 1,234.56") == 1234.56
    assert money("22.17") == 22.17
    assert money(22.17) == 22.17


def test_money_handles_none():
    assert money(None) == 0.0


def test_money_handles_invalid_input():
    assert money("abc") == 0.0
    assert money("") == 0.0
    assert money("$$$") == 0.0
