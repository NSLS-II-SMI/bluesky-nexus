from tempfile import mkdtemp

import pytest
from ophyd_async import sim
from ophyd_async.core import StaticPathProvider, UUIDFilenameProvider, init_devices

import bluesky.plans as bp

import asyncio
import os

import numpy as np
import packaging
import pytest

from bluesky.run_engine import RunEngine, TransitionError


@pytest.fixture(scope="function")
def RE(request):
    loop = asyncio.new_event_loop()
    loop.set_debug(True)
    RE = RunEngine({}, call_returns_result=request.param, loop=loop)

    def clean_event_loop():
        if RE.state not in ("idle", "panicked"):
            try:
                RE.halt()
            except TransitionError:
                pass
        loop.call_soon_threadsafe(loop.stop)
        RE._th.join()
        loop.close()

    request.addfinalizer(clean_event_loop)
    return RE


@pytest.fixture(autouse=True, params=["1", None])
def _strict_debug(monkeypatch, request):
    if request.param is not None:
        monkeypatch.setenv("BLUESKY_DEBUG_CALLBACKS", request.param)
    else:
        monkeypatch.delenv("BLUESKY_DEBUG_CALLBACKS", raising=False)


def test_hdf5_1d(RE):
    pattern_generator = sim.PatternGenerator()
    path_provider = StaticPathProvider(UUIDFilenameProvider(), mkdtemp())
    with init_devices():
        bdet = sim.SimBlobDetector(path_provider, pattern_generator)

    RE(bp.count([bdet], num=5))


def test_hdf5_2d(RE):
    pattern_generator = sim.PatternGenerator()
    path_provider = StaticPathProvider(UUIDFilenameProvider(), mkdtemp())
    with init_devices():
        bdet = sim.SimBlobDetector(path_provider, pattern_generator)

    RE(bp.count([bdet], num=5))