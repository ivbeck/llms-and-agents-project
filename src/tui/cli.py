from __future__ import annotations

import argparse
import asyncio

from src.config import Settings
from src.tui.dashboard import Dashboard


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rag-tui", description="Parallel Question TUI")
    return parser


async def run_tui(settings: Settings) -> None:
    app = Dashboard(settings)
    await app.run_async()


def main() -> None:
    settings = Settings()
    asyncio.run(run_tui(settings))
