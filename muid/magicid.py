# SPDX-License-Identifier: Apache-2.0
"""
Tools for working with MUID.
"""

import os
import threading
import time
from datetime import datetime
from types import NoneType
from typing import Any, AnyStr, Final, Optional, Self, Union

MAX_COUNTER: Final[int] = 8191
EPOCH_START: Final[int] = 1772312400000  # 1st march of 2026


class InvalidMagicID(Exception):
    """Raised when got invalid MagicID."""

    def __init__(self, muid: AnyStr) -> None:
        self.muid = muid

    def __str__(self) -> str:
        return f"Invalid MagicID: {self.muid}"


class MagicID:
    """
    MagicID (MUID) base implementation.
    TODO: Should be implemented in C.
    """

    @staticmethod
    def __timestamp() -> int:
        return int(time.time_ns() // 1_000_000) - EPOCH_START

    @staticmethod
    def __random(n: int) -> bytes:
        return os.urandom(n)

    _proc_fn = int.from_bytes(__random(3), "big") & 0x1FFFF
    _last_ms = __timestamp()
    _counter = 0
    _lock = threading.Lock()

    __muid: bytes

    __slots__ = ("__muid",)

    def __init__(self, muid: Optional[Any] = None) -> None:
        """
        Initialize a new MagicID.
        :param muid: Optional already generated MagicID.
        :raises InvalidMagicID: Raised if given muid is invalid.

        Create new MagicID or validating given muid.
        A MagicID is 14 bytes unique identifier consists of:
            - 42 bits milliseconds timestamp.
            - 13 bits counter.
            - 17 bits pseudo unique process fingerprint.
            - 40 bits secure random bytes.

        >> MagicID()
        >> 0001-8EA1C900-0F6F8410-1E7C1CA4

        >> MagicID("0001-8EA1C900-9D6F84CC-74E81A7A")
        >> 0001-8EA1C900-9D6F84CC-74E81A7A

        >> MagicID(b"\x00\x01\x8f\xadV\xc0\xca\xaf\xd8\x06\x08\xa1\xd2)")
        >> 0001-8FAD56C0-CAAFD806-08A1D229
        """
        if muid is None:
            self.__muid = self.__magic()
        elif isinstance(muid, bytes) and len(muid) == 14:
            self.__muid = muid
        else:
            self.__validate(muid)

    @property
    def raw(self) -> bytes:
        """Return binary MagicID representation."""
        return self.__muid

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, MagicID):
            return self.__muid == other.raw
        elif self.is_valid(other):
            return self.__muid == MagicID(other).raw
        else:
            raise NotImplementedError

    def __ne__(self, other: Any) -> bool:
        if isinstance(other, MagicID):
            return self.__muid != other.raw
        elif self.is_valid(other):
            return self.__muid != MagicID(other).raw
        else:
            raise NotImplementedError

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, MagicID):
            return self.__muid > other.raw
        elif self.is_valid(other):
            return self.__muid > MagicID(other).raw
        else:
            raise NotImplementedError

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, MagicID):
            return self.__muid < other.raw
        elif self.is_valid(other):
            return self.__muid < MagicID(other).raw
        else:
            raise NotImplementedError

    def __len__(self) -> int:
        return 31

    def __validate(self, muid: Any) -> None:
        """
        Validate given muid.
        :param muid: muid to validate.
        :raises InvalidMagicID: Raised if given muid is invalid.
        """

        if isinstance(muid, MagicID):
            self.__muid = muid.raw
        elif isinstance(muid, str):
            if len(muid) == 31:
                try:
                    self.__muid = bytes.fromhex(muid.replace("-", "").lower())
                except (TypeError, ValueError):
                    raise InvalidMagicID(muid)
            else:
                raise InvalidMagicID(muid)
        else:
            raise InvalidMagicID(muid)

    @classmethod
    def is_valid(cls, muid: Any) -> bool:
        """
        Return True if given muid is valid, otherwise False.
        :param muid: muid to validate.
        :return: is valid or not.
        """

        if isinstance(muid, NoneType):
            return False

        try:
            cls(muid)
        except InvalidMagicID:
            return False
        else:
            return True

    @classmethod
    def from_datetime(cls, date_or_ts: Union[datetime, int]) -> Self:
        """
        Create a new MagicID from a given datetime or timestamp.
        :param date_or_ts: datetime or ms timestamp.
        :return: new MagicID.
        """

        if isinstance(date_or_ts, datetime):
            ts = int(date_or_ts.timestamp() * 1000)
        elif isinstance(date_or_ts, int):
            if date_or_ts >= 2**42:
                raise ValueError(
                    f"Timestamp {date_or_ts} is too big. Must be lower than 2^42."
                )
            ts = date_or_ts
        else:
            raise TypeError(f"Expected datetime or int but got {type(date_or_ts)}")

        return cls(cls.__magic(ts=ts))

    @classmethod
    def __magic(cls, *, ts: Optional[int] = None) -> bytes:
        with cls._lock:
            ts = ts or cls.__timestamp()
            if cls._last_ms == ts:
                cls._counter += 1
                if cls._counter > MAX_COUNTER:
                    ms = cls.__timestamp()
                    while ts == ms:
                        ms = cls.__timestamp()
                    ts = ms
                    cls._counter = 0
            else:
                cls._counter = 0

            cls._last_ms = ts

            rand = int.from_bytes(cls.__random(5), "big")

            val = (
                (ts & 0x3FFFFFFFFFF) << 70
                | (cls._counter & 0x1FFF) << 57
                | (cls._proc_fn & 0x1FFFF) << 40
                | (rand & 0xFFFFFFFFFF)
            )

            return val.to_bytes(14, "big")

    def __str__(self) -> str:
        h = self.__muid.hex().upper()
        return f"{h[:4]}-{h[4:12]}-{h[12:20]}-{h[20:]}"

    def __repr__(self) -> str:
        return f"MagicID({self.__str__()})"

    def __bytes__(self) -> bytes:
        return self.__muid
