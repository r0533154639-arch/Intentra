from pathlib import Path
from urllib.parse import urlparse

import httpx


ROOT = Path(__file__).resolve().parents[1]
MODEL_DIRECTORY = ROOT / "models"
MODELS = {
    "face_landmarker.task": (
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
        "face_landmarker/float16/latest/face_landmarker.task"
    ),
    "hand_landmarker.task": (
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
        "hand_landmarker/float16/latest/hand_landmarker.task"
    ),
}
MAX_MODEL_SIZE = 50 * 1024 * 1024


def download_model(client: httpx.Client, name: str, url: str) -> None:
    if urlparse(url).hostname != "storage.googleapis.com":
        raise ValueError(f"Unexpected model host for {name}")
    destination = MODEL_DIRECTORY / name
    temporary = destination.with_suffix(".task.download")
    total = 0
    MODEL_DIRECTORY.mkdir(parents=True, exist_ok=True)
    try:
        with client.stream("GET", url) as response:
            response.raise_for_status()
            with temporary.open("wb") as output:
                for chunk in response.iter_bytes():
                    total += len(chunk)
                    if total > MAX_MODEL_SIZE:
                        raise ValueError(f"Model exceeds the maximum permitted size: {name}")
                    output.write(chunk)
        if total == 0:
            raise ValueError(f"Downloaded model is empty: {name}")
        temporary.replace(destination)
        print(f"Downloaded {name} ({total} bytes)")
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> None:
    with httpx.Client(follow_redirects=True, timeout=60) as client:
        for name, url in MODELS.items():
            download_model(client, name, url)


if __name__ == "__main__":
    main()
