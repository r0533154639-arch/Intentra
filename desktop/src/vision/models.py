from pathlib import Path


MODEL_DIRECTORY = Path(__file__).resolve().parents[2] / "models"
FACE_LANDMARKER_MODEL = MODEL_DIRECTORY / "face_landmarker.task"
HAND_LANDMARKER_MODEL = MODEL_DIRECTORY / "hand_landmarker.task"


def require_model(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(
            f"MediaPipe model is missing: {path}. Run `python scripts/download_models.py` "
            "from the desktop directory."
        )
    return path
