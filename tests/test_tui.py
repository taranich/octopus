import pytest
from tui.tui import OctopusApp, TentacleManager, TentacleWidget

def test_app_tentacle_discovery():
    manager = TentacleManager()
    app = OctopusApp(tentacle_manager=manager)
    assert len(manager.get_tentacles()) >= 2
    assert len(app.widgets) == len(manager.get_tentacles())

def test_tentacle_widget_init():
    manager = TentacleManager()
    tentacle = list(manager.get_tentacles())[0]
    widget = TentacleWidget(tentacle)
    assert widget.tentacle == tentacle
    assert tentacle.name in widget.name_txt.text
