from actions.action_registry import ActionRegistry
from input_control.mouse_controller import MouseController


class ActionDispatcher:
    def __init__(self, mouse_controller: MouseController | None = None):
        self.registry = ActionRegistry(mouse_controller)

    def dispatch(self, event_name: str, context: dict | None = None):
        action = self.registry.get(event_name)
        if action is None:
            raise KeyError(f"No registered action for {event_name}")
        return action.execute(context or {})
