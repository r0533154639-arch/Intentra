from actions.action_dispatcher import ActionDispatcher


class RecordingMouseController:
    def __init__(self):
        self.calls = []

    def move(self, x, y):
        self.calls.append(("move", x, y))

    def click(self):
        self.calls.append(("click",))

    def double_click(self):
        self.calls.append(("double_click",))

    def right_click(self):
        self.calls.append(("right_click",))

    def scroll(self, amount):
        self.calls.append(("scroll", amount))

    def fast_scroll(self, amount, duration_ms, stop_event):
        self.calls.append(("fast_scroll", amount, duration_ms))


def test_dispatcher_routes_all_approved_mouse_actions():
    mouse = RecordingMouseController()
    dispatcher = ActionDispatcher(mouse)

    dispatcher.dispatch("MOVE_CURSOR", {"x": 20, "y": 30})
    dispatcher.dispatch("LEFT_CLICK")
    dispatcher.dispatch("DOUBLE_CLICK")
    dispatcher.dispatch("RIGHT_CLICK")
    dispatcher.dispatch("SCROLL", {"mode": "precise", "amount": 1.5})
    dispatcher.dispatch(
        "SCROLL",
        {"mode": "fast", "amount": 2.0, "duration_ms": 200, "cancel_event": object()},
    )

    assert mouse.calls == [
        ("move", 20, 30),
        ("click",),
        ("double_click",),
        ("right_click",),
        ("scroll", 1.5),
        ("fast_scroll", 2.0, 200),
    ]
