"""Shallow tests that make sure we can at least import the code."""


def test_import_app() -> None:
    """Test import app"""
    from stack.app.main import app  # noqa: F401
