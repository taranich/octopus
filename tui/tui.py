import importlib
import pkgutil
import inspect
from pathlib import Path
import asyncio
import urwid

from tentacles.base_tentacle import BaseTentacle


class TentacleManager:
    def __init__(self, tentacle_package="tentacles"):
        self.tentacle_package = tentacle_package
        self.tentacles = self._discover_tentacles()

    def _discover_tentacles(self):
        tentacles = {}
        try:
            package = importlib.import_module(self.tentacle_package)
            for submodule_info in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
                if "base_tentacle" in submodule_info.name:
                    continue
                
                try:
                    module = importlib.import_module(submodule_info.name)
                    for name, obj in inspect.getmembers(module):
                        if name.lower().endswith("tentacle") and inspect.isclass(obj) and issubclass(obj, BaseTentacle) and obj is not BaseTentacle:
                            tentacle_instance = obj()
                            tentacles[tentacle_instance.name] = tentacle_instance
                except (ImportError, SyntaxError):
                    continue
        except ImportError:
            pass
        return tentacles

    def get_tentacles(self):
        return self.tentacles.values()


class TentacleWidget(urwid.WidgetWrap):
    def __init__(self, tentacle: BaseTentacle):
        self.tentacle = tentacle
        self.animation_frame = 0
        self.animation_chars = ['.  ', ' . ', '  .', ' . ']
        
        self.name_txt = urwid.Text(f" {self.tentacle.name}", wrap='clip')
        self.status_txt = urwid.Text(self.tentacle.get_detailed_status(), wrap='clip')
        self.anim_txt = urwid.Text("- ")

        # Layout: [spinner] [name] [status]
        self.columns = urwid.Columns([
            (4, self.anim_txt),
            (25, self.name_txt),
            self.status_txt
        ])
        
        super().__init__(urwid.AttrMap(self.columns, None, focus_map='reversed'))

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key

    def update(self):
        status = self.tentacle.get_status()
        detailed_status = self.tentacle.get_detailed_status()

        attr = None
        if status == "Running":
            self.animation_frame = (self.animation_frame + 1) % len(self.animation_chars)
            attr = 'running'
            spinner = f"{self.animation_chars[self.animation_frame]} "
        elif status == "Error":
            attr = 'error'
            spinner = "ERR "
        elif status == "Stopping":
            attr = 'stopping'
            spinner = "- "
        else:
            spinner = "- "

        self.anim_txt.set_text((attr, spinner) if attr else spinner)
        self.status_txt.set_text((attr, detailed_status) if attr else detailed_status)


class OctopusApp:
    palette = [
        # name, fore_16, back_16, mono, fore_high, back_high
        (None, 'light gray', 'black', None, '#ebdbb2', '#282828'),
        ('header', 'black,bold', 'dark cyan', 'bold', '#282828,bold', '#8ec07c'),
        ('footer', 'light gray', 'dark gray', None, '#a89984', '#3c3836'),
        ('reversed', 'black', 'yellow', 'standout', '#282828', '#fabd2f'),
        ('running', 'light green', 'black', None, '#b8bb26', '#282828'),
        ('error', 'light red', 'black', None, '#fb4934', '#282828'),
        ('stopping', 'yellow', 'black', None, '#fe8019', '#282828'),
    ]

    def __init__(self, tentacle_manager: TentacleManager = None):
        self.manager = tentacle_manager or TentacleManager()
        self.widgets = [TentacleWidget(t) for t in self.manager.get_tentacles()]
        self.list_box = urwid.ListBox(urwid.SimpleFocusListWalker(self.widgets))
        
        header = urwid.AttrMap(urwid.Text(" Octopus Tentacle Manager", align='left'), 'header')
        footer = urwid.AttrMap(urwid.Text(" Q: Quit | S: Start/Stop | R: Reset | Space: Toggle All"), 'footer')
        
        self.top = urwid.Frame(self.list_box, header=header, footer=footer)
        self.loop = None

    def run(self):
        screen = urwid.raw_display.Screen()
        if hasattr(screen, 'set_terminal_256color'):
            screen.set_terminal_256color()

        ev_loop = urwid.AsyncioEventLoop(loop=asyncio.get_event_loop())
        self.loop = urwid.MainLoop(
            self.top, 
            self.palette, 
            screen=screen,
            event_loop=ev_loop,
            unhandled_input=self.handle_input,
            handle_mouse=False,
            input_filter=self._strict_input_filter
        )
        self.update_ui(self.loop, None)
        self.loop.run()

    def _strict_input_filter(self, keys, raw):
        return [k for k in keys if not urwid.is_mouse_event(k)]

    def update_ui(self, loop, data):
        for widget in self.widgets:
            widget.update()
        self.loop.set_alarm_in(0.2, self.update_ui)

    def handle_input(self, key):
        if key in ('q', 'Q'):
            asyncio.create_task(self.shutdown())
        elif key in ('s', 'S'):
            self.toggle_selected()
        elif key in ('r', 'R'):
            self.reset_selected()
        elif key == ' ':
            self.toggle_all()

    def toggle_selected(self):
        widget = self.list_box.focus
        if widget:
            t = widget.tentacle
            if t.get_status() == "Running":
                asyncio.create_task(t.stop())
            else:
                asyncio.create_task(t.start())

    def reset_selected(self):
        widget = self.list_box.focus
        if widget:
            asyncio.create_task(widget.tentacle.reset())

    def toggle_all(self):
        tentacles = self.manager.get_tentacles()
        any_running = any(t.get_status() == "Running" for t in tentacles)
        for t in tentacles:
            if any_running:
                asyncio.create_task(t.stop())
            else:
                asyncio.create_task(t.start())

    async def shutdown(self):
        for t in self.manager.get_tentacles():
            await t.stop()
        def quit(*args):
            raise urwid.ExitMainLoop()
        self.loop.set_alarm_in(0, quit)
