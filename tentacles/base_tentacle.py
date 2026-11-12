import json
import logging
from abc import ABC, abstractmethod
import asyncio
from pathlib import Path
import inspect

class BaseTentacle(ABC):
    def __init__(self, name: str):
        self.name = name
        self.tentacle_dir = Path(inspect.getfile(self.__class__)).parent
        self._task: asyncio.Task | None = None
        self._status: int = 0  # 0: stopped, 1: running, 2: stopping, 3: error
        self._detailed_status: str = ""
        self.stop_event = asyncio.Event()
        self.state_file = self.tentacle_dir / f"{name}_state.json"
        self.logger = self._setup_logger()
        self.update_detailed_status("Idle")

    def _setup_logger(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(self.tentacle_dir / f"{self.name}.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    async def start(self):
        if self._task and not self._task.done():
            self.logger.warning("Tentacle is already running.")
            return

        self.stop_event.clear()
        self._task = asyncio.create_task(self.run())
        self._status = 1
        self.logger.info("Tentacle started.")

    async def stop(self):
        if not self._task or self._task.done():
            self.logger.warning("Tentacle is not running.")
            return

        self.logger.info("Stopping tentacle...")
        self._status = 2
        self.stop_event.set() # Signal the task to stop
        try:
            await asyncio.wait_for(self._task, timeout=10)
        except asyncio.TimeoutError:
            self._task.cancel()
            self.logger.warning("Tentacle task cancelled forcefully due to timeout.")
        self._status = 0
        self.update_detailed_status("Idle")
        self.logger.info("Tentacle stopped.")

    async def reset(self):
        self.logger.info("Resetting tentacle state.")
        if self._task and not self._task.done():
            await self.stop()
        if self.state_file.exists():
            self.state_file.unlink()
            self.logger.info("State file removed.")
        self.update_detailed_status("Idle")

    @abstractmethod
    async def run(self):
        pass

    def save_state(self, data):
        with open(self.state_file, 'w') as f:
            json.dump(data, f)
        self.logger.info(f"State saved to {self.state_file}")

    def load_state(self):
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                self.logger.info(f"Loading state from {self.state_file}")
                return json.load(f)
        return None

    def get_status(self):
        if self._status == 1:
            return "Running"
        elif self._status == 2:
            return "Stopping"
        elif self._status == 3:
            return "Error"
        else:
            return "Stopped"

    def update_detailed_status(self, message: str):
        self._detailed_status = message.replace('\n', ' ')[:100] # Truncate and remove newlines

    def get_detailed_status(self) -> str:
        return self._detailed_status
