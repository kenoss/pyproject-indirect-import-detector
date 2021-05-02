from typing import TypeVar, cast

from result import Err as Err_
from result import Ok as Ok_
from result import Result

__all__ = [
    "Result",
    "Ok",
    "Err",
]


T = TypeVar("T")
E = TypeVar("E")
E_ = TypeVar("E_")


class Ok(Ok_[T]):
    def wrap_err(self, _err: E_) -> "Ok[T]":
        return self


class Err(Err_[E]):
    def wrap_err(self, err: E_) -> "Err[E_]":  # where E: BaseException, E_: baseException
        assert isinstance(self._value, BaseException)
        assert isinstance(err, BaseException)

        try:
            raise err from self._value
        except Exception as err:
            return Err(cast(E_, err))
