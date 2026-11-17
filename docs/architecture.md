# Architecture overview

Intentra is implemented as a three-part system:

1. Desktop app: camera input, gaze estimation, gesture classification, and OS-level mouse actions.
2. Web app: account management and settings UI.
3. Backend: FastAPI API, authentication, storage, settings synchronization, and updates.

The design deliberately separates detection from action execution. A gesture detector emits internal events that are routed through an action dispatcher to an action registry and then to a mouse controller.
