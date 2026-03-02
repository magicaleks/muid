import time
from datetime import datetime

import pytest

from muid import MagicID
from tests.conftest import FakeClock, unpack_id


def test_muid():
    muid = MagicID()
    muid_2 = MagicID()
    assert len(muid.raw) == 14
    assert muid == muid
    assert muid_2 != muid
    assert muid_2 > muid
    assert muid < muid_2
    assert muid == MagicID(muid) == MagicID(muid.raw)
    assert muid.raw == bytes(muid)


def test_counter():
    clock = FakeClock(start_ms=1000)

    original = time.time_ns
    time.time_ns = clock.time_ns

    try:
        ids = []
        for _ in range(8192):
            muid = MagicID()
            assert muid not in ids
            ids.append(muid)

        assert ids == sorted(ids)
        decoded = [unpack_id(id_.raw) for id_ in ids]
        assert all(d[0] == decoded[0][0] for d in decoded)
        assert decoded[-1][1] == 8191

        clock.advance_ms(1)
        next_id = MagicID()
        next_decoded = unpack_id(next_id.raw)

        assert next_decoded[0] - 1 == decoded[0][0]
        assert next_decoded[1] == 0

    finally:
        time.time_ns = original


def test_monotonic():
    arr = []
    for _ in range(10000):
        muid = MagicID()
        assert muid not in arr
        arr.append(muid)

    assert arr == sorted(arr)


def test_from_datetime():
    muid = MagicID.from_datetime(1000 * 1000)
    assert unpack_id(muid.raw)[0] == 1000000
    muid = MagicID.from_datetime(datetime.fromtimestamp(1000))
    assert unpack_id(muid.raw)[0] == 1000000
    with pytest.raises(ValueError):
        MagicID.from_datetime(2**42)


def test_is_valid():
    muid = MagicID()
    assert MagicID.is_valid(muid)
    assert MagicID.is_valid(muid.raw)
    assert MagicID.is_valid(str(muid))
    assert not MagicID.is_valid(None)
