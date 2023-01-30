"""jyg metadata tests."""
import jyg


def test_version() -> None:
    """Verify it has a version."""
    assert jyg.__version__, "no version"


def test_js() -> None:
    """Verify it has js metadata."""
    assert jyg.__js__, "no js metadata"


def test_magic_lab_extensions() -> None:
    """Verify it has the right number of labextensions."""
    assert len(jyg._jupyter_labextension_paths()) == 1, "too many/few labextensions"


def test_magic_server_extensions() -> None:
    """Verify it has the right number of labextensions."""
    assert (
        len(jyg._jupyter_server_extension_paths()) == 1
    ), "too many/few server extensions"
