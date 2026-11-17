from __future__ import annotations

import json
from pathlib import Path


class RecentFilesService:
    def __init__(self, file_path: Path, max_items: int = 10) -> None:
        self.file_path = file_path
        self.max_items = max_items

    def load(self) -> list[str]:
        if not self.file_path.exists():
            return []
        payload = json.loads(self.file_path.read_text(encoding="utf-8"))
        return payload.get("recent_files", [])

    def add(self, path: str) -> None:
        files = [x for x in self.load() if x != path]
        files.insert(0, path)
        files = files[: self.max_items]
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(
            json.dumps({"recent_files": files}, indent=2), encoding="utf-8"
        )
