from __future__ import annotations
import argparse
from textual.driver import Driver

from src.config import Settings

class Dashboard:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def run_async(self) -> None:
        pass

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rag-tui", description="Parallel Question TUI")
    return parser

async def run_tui(settings: Settings, driver_class: type[Driver] | None = None) -> None:
    app = Dashboard(settings)
    await app.run_async()

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    settings = Settings()
    import asyncio
    asyncio.run(run_tui(settings))