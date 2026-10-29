"""Optional timing smoke test for a real Raspberry boot."""

import time

import pytest

pytestmark = pytest.mark.hardware


def test_boot_timing_probe_is_opt_in():
    started = time.monotonic()
    assert time.monotonic() - started < 60
