import pytest
from tentacles.dummy_tentacle.dummy_tentacle import DummyTentacle
import time
import asyncio

@pytest.mark.asyncio
async def test_dummy_tentacle_run():
    tentacle = DummyTentacle()
    await tentacle.start()
    await asyncio.sleep(0.1)
    assert tentacle.get_status() == "Running"
    assert "Doing nothing..." in tentacle.get_detailed_status()
    await tentacle.stop()
    assert tentacle.get_status() == "Stopped"
