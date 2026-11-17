from unittest.mock import patch

import pytest

from input_control.mouse_controller import MouseController


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        ((0, 0), (1, 1)),
        ((1919, 0), (1918, 1)),
        ((0, 1079), (1, 1078)),
        ((1919, 1079), (1918, 1078)),
        ((800, 600), (800, 600)),
    ],
)
def test_move_keeps_cursor_inside_the_screen_and_away_from_failsafe_corners(target, expected):
    with (
        patch("input_control.mouse_controller.pyautogui.size", return_value=(1920, 1080)),
        patch("input_control.mouse_controller.pyautogui.moveTo") as move_to,
    ):
        MouseController().move(*target)

    move_to.assert_called_once_with(*expected)
