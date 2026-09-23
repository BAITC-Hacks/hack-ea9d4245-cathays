from dataclasses import dataclass, field
from pathlib import Path
import os
from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parents[1]
ROOT = next(parent for parent in BACKEND_ROOT.parents if (parent / "voice_router_dataset").is_dir())
load_dotenv(BACKEND_ROOT / ".env")

def dataset_path() -> Path:
    configured = os.getenv("VOICE_ROUTER_DATASET_PATH", "").strip()
    # Preserve the original template value after the backend folder move.
    if configured.replace("\\", "/") == "../voice_router_dataset/case_2/voice_router_dataset":
        configured = "voice_router_dataset/case_2/voice_router_dataset"
    path = Path(configured) if configured else Path("voice_router_dataset/case_2/voice_router_dataset")
    return (path if path.is_absolute() else ROOT / path).resolve()

@dataclass(frozen=True)
class Settings:
    dataset_path: Path = field(default_factory=dataset_path)
    provider: str = field(default_factory=lambda: os.getenv("VOICE_ROUTER_PROVIDER", "openai_compatible"))
    model: str = field(default_factory=lambda: os.getenv("VOICE_ROUTER_MODEL", "").strip() or "gpt-4.1-mini")
    base_url: str = field(default_factory=lambda: os.getenv("VOICE_ROUTER_BASE_URL", "").strip() or "https://api.openai.com/v1")
    api_key: str = field(default_factory=lambda: (os.getenv("VOICE_ROUTER_API_KEY") or os.getenv("OPENAI_API_KEY", "")).strip(), repr=False)
    policy_version: str = field(default_factory=lambda: os.getenv("VOICE_ROUTER_POLICY_VERSION", "uncertainty-v1"))
    cors_origins: list[str] = field(default_factory=lambda: [origin.strip() for origin in os.getenv("VOICE_ROUTER_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174").split(",") if origin.strip()])

settings = Settings()
