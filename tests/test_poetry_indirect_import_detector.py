from importlib.metadata import Distribution


def test_version() -> None:
    assert Distribution.from_name("pyproject_indirect_import_detector").version == "0.1.0"
