from actions.base_action import BaseAction


class RightClickAction(BaseAction):
    def __init__(self, mouse_controller):
        self.mouse_controller = mouse_controller

    def execute(self, context):
        self.mouse_controller.right_click()
        return {"status": "right_clicked"}
