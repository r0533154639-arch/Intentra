from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")


@dataclass
class DesktopConfig:
    app_name: str = "Intentra"
    server_base_url: str = "http://localhost:8000"
    cache_path: Path = field(default_factory=lambda: Path.home() / ".intentra" / "settings_cache.db")
    camera_index: int = 0
    update_public_key: str = ""
    debug: bool = False

    @classmethod
    def load(cls) -> "DesktopConfig":
        return cls(
            server_base_url=os.getenv("INTENTRA_API_BASE_URL", "http://localhost:8000").rstrip("/"),
            cache_path=Path(os.getenv("INTENTRA_CACHE_PATH", str(Path.home() / ".intentra" / "settings_cache.db"))),
            camera_index=int(os.getenv("INTENTRA_CAMERA_INDEX", "0")),
            update_public_key=os.getenv("INTENTRA_UPDATE_PUBLIC_KEY", ""),
            debug=os.getenv("INTENTRA_DEBUG", "false").lower() == "true",
        )
