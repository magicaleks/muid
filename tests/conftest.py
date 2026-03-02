from typing import Tuple

MASK_TS = 0x3FFFFFFFFFF
MASK_COUNTER = 0x1FFF
MASK_PROC = 0x1FFFF
MASK_RAND = 0xFFFFFFFFFF


def unpack_id(val: bytes) -> Tuple[int, int, int, int]:
    val = int.from_bytes(val, "big")
    ts = (val >> 70) & MASK_TS
    counter = (val >> 57) & MASK_COUNTER
    proc_fn = (val >> 40) & MASK_PROC
    rand = val & MASK_RAND

    return ts, counter, proc_fn, rand


def pack_id(ts: int, counter: int, proc_fn: int, rand: int) -> bytes:
    return (
        (ts & MASK_TS) << 70
        | (counter & MASK_COUNTER) << 57
        | (proc_fn & MASK_PROC) << 40
        | (rand & MASK_RAND)
    ).to_bytes(14, "big")


class FakeClock:
    def __init__(self, start_ms: int):
        self._ns = start_ms * 1_000_000

    def time_ns(self) -> int:
        return self._ns

    def advance_ms(self, ms: int = 1):
        self._ns += ms * 1_000_000
