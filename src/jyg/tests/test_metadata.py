"""jyg metadata tests."""
import jyg


def test_version():
    assert jyg.__version__, "no version"


def test_js():
    assert jyg.__js__, "no js metadata"


def test_magic_lab_extensions():
    assert len(jyg._jupyter_labextension_paths()) == 1, "too many/few labextensions"
