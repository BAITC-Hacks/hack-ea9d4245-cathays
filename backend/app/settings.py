from dataclasses import dataclass
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[2]

@dataclass(frozen=True)
class Settings:
    dataset_path: Path = Path(os.getenv("VOICE_ROUTER_DATASET_PATH", str(ROOT / "voice_router_dataset/case_2/voice_router_dataset")))
    provider: str = os.getenv("VOICE_ROUTER_PROVIDER", "openai_compatible")
    model: str = os.getenv("VOICE_ROUTER_MODEL", "")
    base_url: str = os.getenv("VOICE_ROUTER_BASE_URL", "")
    api_key: str = os.getenv("VOICE_ROUTER_API_KEY", "")
    policy_version: str = os.getenv("VOICE_ROUTER_POLICY_VERSION", "uncertainty-v1")

settings = Settings()
