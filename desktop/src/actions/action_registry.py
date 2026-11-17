from actions.double_click import DoubleClickAction
from actions.left_click import LeftClickAction
from actions.move_cursor import MoveCursorAction
from actions.right_click import RightClickAction
from actions.scroll_action import ScrollAction
from input_control.mouse_controller import MouseController


class ActionRegistry:
    def __init__(self, mouse_controller: MouseController | None = None):
        self.mouse_controller = mouse_controller or MouseController()
        self.actions = {
            "MOVE_CURSOR": MoveCursorAction(self.mouse_controller),
            "LEFT_CLICK": LeftClickAction(self.mouse_controller),
            "DOUBLE_CLICK": DoubleClickAction(self.mouse_controller),
            "RIGHT_CLICK": RightClickAction(self.mouse_controller),
            "SCROLL": ScrollAction(self.mouse_controller),
        }

    def get(self, name: str):
        return self.actions.get(name)
