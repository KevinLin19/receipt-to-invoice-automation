import json
from pathlib import Path

def load_profile(profile_name: str, profiles_path: str = "profiles.json") -> dict:
    path = Path(profiles_path)
    if not path.exists():
        raise FileNotFoundError("profiles.json not found. Create it from profiles.example.json.")
    data = json.loads(path.read_text(encoding="utf-8"))
    if profile_name not in data:
        raise KeyError(f"Profile '{profile_name}' not found in profiles.json.")
    return data[profile_name]