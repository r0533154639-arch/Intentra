from actions.base_action import BaseAction


class LeftClickAction(BaseAction):
    def __init__(self, mouse_controller):
        self.mouse_controller = mouse_controller

    def execute(self, context):
        self.mouse_controller.click()
        return {"status": "clicked"}
