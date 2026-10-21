"""プロジェクト内の共通パスと時刻のヘルパー。"""

import os
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBLEMS_DIR = ROOT / "problems"
CONFIG_DIR = ROOT / "config"


def review_dir() -> Path:
    # validation時は環境変数で一時ディレクトリに差し替え、本物の履歴を汚さない
    return Path(os.environ.get("PANDAS_PRACTICE_REVIEW_DIR", ROOT / "review"))


def now() -> datetime:
    return datetime.now().astimezone().replace(microsecond=0)
