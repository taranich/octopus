import pytest
from pathlib import Path
import asyncio
from unittest.mock import patch

import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tentacles.base_tentacle import BaseTentacle

class ConcreteTentacle(BaseTentacle):
    def __init__(self, name="test_tentacle"):
        super().__init__(name)
        self.run_called = False

    async def run(self):
        self.run_called = True
        while not self.stop_event.is_set():
            await asyncio.sleep(0.01)

def test_base_tentacle_initialization():
    tentacle = ConcreteTentacle()
    assert tentacle.name == "test_tentacle"
    assert tentacle.get_status() == "Stopped"

@pytest.mark.asyncio
async def test_base_tentacle_start_stop():
    tentacle = ConcreteTentacle()
    
    await tentacle.start()
    assert tentacle.get_status() == "Running"
    assert tentacle._task is not None

    await tentacle.stop()
    assert tentacle.stop_event.is_set()
    assert tentacle.get_status() == "Stopped"

def test_base_tentacle_state(tmp_path):
    tentacle = ConcreteTentacle()
    tentacle.state_file = tmp_path / "state.json"
    
    test_data = {"key": "value"}
    tentacle.save_state(test_data)
    assert tentacle.state_file.exists()
    
    loaded_data = tentacle.load_state()
    assert loaded_data == test_data
