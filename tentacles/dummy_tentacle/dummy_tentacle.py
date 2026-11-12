from tentacles.base_tentacle import BaseTentacle
import asyncio

class DummyTentacle(BaseTentacle):
    def __init__(self):
        super().__init__("dummy_tentacle")

    async def run(self):
        self.logger.info("Dummy tentacle started.")
        self.update_detailed_status("Doing nothing...")
        while not self.stop_event.is_set():
            await asyncio.sleep(1)
        self.logger.info("Dummy tentacle stopped.")
