from actions.base_action import BaseAction


class MoveCursorAction(BaseAction):
    def __init__(self, mouse_controller):
        self.mouse_controller = mouse_controller

    def execute(self, context):
        target_x = int(context["x"])
        target_y = int(context["y"])
        self.mouse_controller.move(target_x, target_y)
        return {"status": "moved", "x": target_x, "y": target_y}
