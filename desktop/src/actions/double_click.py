from actions.base_action import BaseAction


class DoubleClickAction(BaseAction):
    def __init__(self, mouse_controller):
        self.mouse_controller = mouse_controller

    def execute(self, context):
        self.mouse_controller.double_click()
        return {"status": "double_clicked"}
