import time
from datetime import datetime, timedelta
from typing import Any

import pytest

from muid import InvalidMagicID, MagicID
from muid.magicid import EPOCH_START
from tests.conftest import FakeClock, unpack_id


def test_muid():
    muid = MagicID()
    muid_2 = MagicID()
    assert len(muid.raw) == 14
    assert muid == muid
    assert muid_2 != muid
    assert muid_2 > muid
    assert muid < muid_2
    assert muid == MagicID(muid) == MagicID(muid.raw) == MagicID(str(muid))
    assert muid.raw == bytes(muid)


def test_comparison():
    muid = MagicID()
    muid_2 = MagicID()
    assert muid == str(muid)
    assert muid == str(muid).lower()
    assert muid == muid.raw
    assert muid_2 != str(muid)
    assert muid_2 >= muid
    assert muid <= muid_2
    assert sorted([muid_2, muid]) == [muid, muid_2]
    assert {muid: 1}[MagicID(str(muid))] == 1


@pytest.mark.parametrize("other", [None, 1, "", "garbage", b"short", object()])
def test_comparison_foreign(other: Any):
    muid = MagicID()
    assert muid != other
    assert other != muid
    with pytest.raises(TypeError):
        muid < other
    with pytest.raises(TypeError):
        muid >= other


@pytest.mark.parametrize(
    "val",
    [
        "0002A2011D800081B3FFC812A17E",
        "0002A2011D8000----81B3FFC812A17E",
        "0002x977F0200x0300034FxEA9CE3FA",
        "0002-977F0200-0300034F-EA9CE3  ",
        "",
        None,
    ],
)
def test_validation_negative(val: Any):
    with pytest.raises(InvalidMagicID):
        MagicID(val)


def test_counter():
    clock = FakeClock(start_ms=time.time_ns() // 1_000_000 + 1)

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
    muid = MagicID.from_datetime(EPOCH_START + 1000 * 1000)
    assert unpack_id(muid.raw)[0] == 1000000
    muid = MagicID.from_datetime(datetime.fromtimestamp(EPOCH_START / 1000 + 1000))
    assert unpack_id(muid.raw)[0] == 1000000
    assert unpack_id(MagicID.from_datetime(EPOCH_START).raw)[0] == 0
    with pytest.raises(ValueError):
        MagicID.from_datetime(EPOCH_START + 2**42)
    with pytest.raises(ValueError):
        MagicID.from_datetime(EPOCH_START - 1)


def test_from_datetime_order():
    now = datetime.now()
    muid = MagicID()
    assert MagicID.from_datetime(now - timedelta(seconds=1)) < muid
    assert MagicID.from_datetime(now + timedelta(seconds=1)) > muid


def test_is_valid():
    muid = MagicID()
    assert MagicID.is_valid(muid)
    assert MagicID.is_valid(muid.raw)
    assert MagicID.is_valid(str(muid))
    assert not MagicID.is_valid(None)
