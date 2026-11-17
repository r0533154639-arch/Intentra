from __future__ import annotations

import threading
import time
from math import trunc

import pyautogui


class MouseController:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0
        self._scroll_remainder = 0.0
        self.sensitivity = 1.0

    def move(self, x: int, y: int) -> None:
        pyautogui.moveTo(x, y)

    def click(self) -> None:
        pyautogui.click()

    def double_click(self) -> None:
        pyautogui.doubleClick()

    def right_click(self) -> None:
        pyautogui.rightClick()

    def scroll(self, amount: float) -> None:
        total = amount + self._scroll_remainder
        whole_steps = trunc(total)
        self._scroll_remainder = total - whole_steps
        if whole_steps:
            pyautogui.scroll(whole_steps)

    def fast_scroll(self, amount: float, duration_ms: int, stop_event: threading.Event) -> None:
        if duration_ms <= 0:
            raise ValueError("Fast-scroll duration must be greater than zero")
        steps = max(1, min(30, duration_ms // 20))
        interval = duration_ms / steps / 1000.0
        emitted = 0.0
        for index in range(steps):
            if stop_event.is_set():
                return
            target = amount * (index + 1) / steps
            self.scroll(target - emitted)
            emitted = target
            deadline = time.monotonic() + interval
            while not stop_event.is_set():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                stop_event.wait(remaining)
