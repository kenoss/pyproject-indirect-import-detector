__all__ = [
    "InvalidPyProjectError",
    "InvalidPythonVersionError",
]


class InvalidPyProjectError(Exception):
    def __init__(self, message: str) -> None:
        message = "pyproject.toml: " + message
        super().__init__(message)


class InvalidPythonVersionError(InvalidPyProjectError):
    def __init__(self, message: str) -> None:
        message = '"tool/poetry/dependencies/python": ' + message
        super().__init__(message)
