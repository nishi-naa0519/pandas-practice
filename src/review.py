"""感想(自由記述)を review/notes.yaml に履歴として追記する。

    from src.review import save_review
    memo = "groupbyの書き方がまだ曖昧"
    save_review("P012", memo)
"""

import textwrap
from datetime import datetime, timedelta

import yaml

from src.paths import now, review_dir

DEDUP_WINDOW = timedelta(minutes=5)


class _Dumper(yaml.SafeDumper):
    pass


def _str_representer(dumper, value):
    # 複数行の感想は改行を保ったまま読めるよう literal block (|) で書く
    style = "|" if "\n" in value else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


_Dumper.add_representer(str, _str_representer)


def load_reviews():
    path = review_dir() / "notes.yaml"
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("reviews") or []


def save_review(problem_id, memo):
    text = _clean(memo)
    if not text:
        print("感想が空なので保存しませんでした")
        return

    current = now()
    for r in reversed(load_reviews()):
        if r.get("problem_id") != problem_id or _clean(r.get("impression", "")) != text:
            continue
        if current - datetime.fromisoformat(str(r["timestamp"])) < DEDUP_WINDOW:
            print(f"Already saved: {problem_id} (直前と同じ内容なので保存しませんでした)")
            return

    entry = {"problem_id": problem_id, "timestamp": current.isoformat(), "impression": text}
    _append(entry)
    print(f"Saved review: {problem_id}")


def _clean(memo):
    lines = textwrap.dedent(str(memo)).strip().splitlines()
    return "\n".join(line.rstrip() for line in lines)


def _append(entry):
    path = review_dir() / "notes.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if not existing.strip() or yaml.safe_load(existing) in (None, {"reviews": None}, {"reviews": []}):
        existing = "reviews:\n"
    if not existing.endswith("\n"):
        existing += "\n"

    dumped = yaml.dump([entry], Dumper=_Dumper, allow_unicode=True, sort_keys=False, width=10**6)
    block = "\n" + textwrap.indent(dumped, "  ")

    # 追記後もYAMLとして正しく読めることを確認してから書き込む
    before = len((yaml.safe_load(existing) or {}).get("reviews") or [])
    after = (yaml.safe_load(existing + block) or {}).get("reviews") or []
    if len(after) != before + 1 or after[-1]["impression"] != entry["impression"]:
        raise RuntimeError("notes.yaml への追記に失敗しました(ファイルは変更していません)")
    path.write_text(existing + block, encoding="utf-8")
