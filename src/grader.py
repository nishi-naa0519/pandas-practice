"""Notebook から使う採点・ヒント・履歴記録。

    from src.grader import check, hint, done

    check("P001", solve)   # coding 問題の採点(結果を review/history.csv に記録)
    hint("P001")           # ヒントを1つずつ表示(使ったことは履歴に残る)
    done("P006")           # exploration 問題を終えたことを記録
"""

import csv
import importlib.util
import sys
from datetime import datetime, timedelta

import pandas as pd
import yaml

from src.paths import PROBLEMS_DIR, now, review_dir
from src.testing import compare

HISTORY_COLUMNS = ["problem_id", "timestamp", "passed", "hint_used", "score"]
DEDUP_WINDOW = timedelta(minutes=5)

# この kernel で表示したヒントの数 {problem_id: n}
_hints_shown: dict[str, int] = {}


# ---------- 採点 ----------

def run_tests(problem_id, solve):
    """全ケースを実行し [(case, reason or None, got)] を返す。記録はしない。"""
    tests = _load_tests(problem_id)
    normalize = getattr(tests, "normalize", None)
    results = []
    for c in tests.make_cases():
        try:
            got = solve(*c["args"].values())
        except Exception as e:  # 解答のエラーは採点結果として扱う
            results.append((c, f"エラー: {type(e).__name__}: {e}", None))
            continue
        checked = normalize(got) if normalize and got is not None else got
        results.append((c, compare(checked, c["expected"], **c["options"]), got))
    return results


def check(problem_id, solve, *, record=True):
    results = run_tests(problem_id, solve)
    n_ok = sum(reason is None for _, reason, _ in results)
    passed = n_ok == len(results)

    for c, reason, _ in results:
        print(f"{'✅' if reason is None else '❌'} {c['name']}")
    first_fail = next(((c, reason, got) for c, reason, got in results if reason is not None), None)
    if first_fail:
        _show_case(*first_fail)

    print()
    if passed:
        print(f"🎉 正解！ ({n_ok}/{len(results)})")
    else:
        print(f"もう少し！ ({n_ok}/{len(results)})  solve(...) を直接実行して出力を確かめてみましょう")

    if record:
        _record(problem_id, passed, f"{n_ok}/{len(results)}")


def done(problem_id):
    """exploration 問題を終えたことを記録する(自己申告)。"""
    if _record(problem_id, True, "exploration"):
        print(f"Recorded: {problem_id}  solution.ipynb で確認項目を見比べてみましょう")
    else:
        print(f"Already recorded: {problem_id}")


def _show_case(c, reason, got):
    print(f"\n--- 「{c['name']}」の詳細 ---")
    print(reason + "\n")
    for name, value in c["args"].items():
        if isinstance(value, (pd.DataFrame, pd.Series)):
            print(f"[入力 {name}]\n{value}\n")
    print(f"[期待される出力]\n{c['expected']}\n")
    print(f"[あなたの出力]\n{got}")


def _load_tests(problem_id):
    path = PROBLEMS_DIR / problem_id / "tests.py"
    if not path.exists():
        raise FileNotFoundError(f"{problem_id} のテストが見つかりません: {path}")
    spec = importlib.util.spec_from_file_location(f"tests_{problem_id}", path)
    module = importlib.util.module_from_spec(spec)
    # 問題フォルダに __pycache__ を作らない
    prev, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = prev
    return module


# ---------- ヒント ----------

def hint(problem_id):
    path = PROBLEMS_DIR / problem_id / "content.yaml"
    hints = yaml.safe_load(path.read_text(encoding="utf-8")).get("hints") or []
    if not hints:
        print("この問題にはヒントがありません")
        return
    n = min(_hints_shown.get(problem_id, 0), len(hints) - 1)
    _hints_shown[problem_id] = n + 1
    print(f"💡 ヒント {n + 1}/{len(hints)}: {hints[n]}")


# ---------- 履歴 ----------

def _record(problem_id, passed, score):
    """history.csv に1行追記する。直近5分以内に同じ結果を記録済みならスキップして False を返す。"""
    path = review_dir() / "history.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "problem_id": problem_id,
        "timestamp": now().isoformat(),
        "passed": str(passed).lower(),
        "hint_used": str(_hints_shown.get(problem_id, 0) > 0).lower(),
        "score": score,
    }
    last = _last_row(path, problem_id)
    if last is not None:
        same = all(last.get(k) == row[k] for k in ["passed", "hint_used", "score"])
        recent = now() - datetime.fromisoformat(last["timestamp"]) < DEDUP_WINDOW
        if same and recent:
            return False

    new_file = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HISTORY_COLUMNS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)
    return True


def _last_row(path, problem_id):
    if not path.exists():
        return None
    with path.open(newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["problem_id"] == problem_id]
    return rows[-1] if rows else None
