from actions.base_action import BaseAction


class ScrollAction(BaseAction):
    def __init__(self, mouse_controller):
        self.mouse_controller = mouse_controller

    def execute(self, context):
        amount = context.get("amount", 0)
        if context.get("mode") == "fast":
            self.mouse_controller.fast_scroll(
                float(amount),
                int(context["duration_ms"]),
                context["cancel_event"],
            )
        else:
            self.mouse_controller.scroll(float(amount))
        return {"status": "scrolled", "amount": amount}
