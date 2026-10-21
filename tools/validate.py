"""プロジェクト全体の機械的なチェック。

    uv run python tools/validate.py             # 通常のチェック(数秒)
    uv run python tools/validate.py --execute   # 全Notebookを実際に実行するチェックも行う(数分)

本物の review/ は変更しない(採点・感想保存のテストは一時ディレクトリで行う)。
"""

import contextlib
import io
import os
import re
import sys
import tempfile
from collections import Counter
from datetime import timedelta
from pathlib import Path

import nbformat
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import grader, review  # noqa: E402

PROBLEMS = ROOT / "problems"
REQUIRED_META = [
    "id", "title", "category", "problem_type", "difficulty", "learning_level", "primary_tags",
    "secondary_tags", "curriculum_items", "estimated_minutes", "prerequisites", "source_type", "variant_of",
]
# Write 対象外の API。solution / exercise のコードセルに出てきたら警告する
BANNED = {
    r"\.query\(": "query", r"\.apply\(": "apply", r"\.transform\(": "transform", r"pivot_table": "pivot_table",
    r"\.melt\(": "melt", r"\.stack\(": "stack", r"\.unstack\(": "unstack", r"\.rolling\(": "rolling",
    r"\.expanding\(": "expanding", r"\.resample\(": "resample", r"\.eval\(": "eval", r"\.xs\(": "xs",
    r"MultiIndex": "MultiIndex", r"\blambda\b": "lambda", r"\.pipe\(": "pipe", r"\.assign\(": "assign",
}

errors, warnings = [], []


def error(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def section(title):
    print(f"\n== {title}")


def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def code_cells(nb, tag=None):
    return [c.source for c in nb.cells if c.cell_type == "code" and (tag is None or tag in c.metadata.get("tags", []))]


# ---------------------------------------------------------------- 設定ファイル

def check_config():
    section("config")
    tags_cfg = load_yaml(ROOT / "config" / "tags.yaml")
    tags = set()
    for kind, prefix in [("methods", "method:"), ("syntax", "syntax:"), ("tasks", "task:"), ("concepts", "concept:")]:
        for t in tags_cfg[kind]:
            if not re.fullmatch(prefix + r"[a-z][a-z0-9_]*", t["id"]):
                error(f"tags.yaml: 命名規則違反 {t['id']}")
            if t["id"] in tags:
                error(f"tags.yaml: 重複 {t['id']}")
            tags.add(t["id"])
    cur = load_yaml(ROOT / "config" / "curriculum.yaml")
    items = {}
    for it in cur["items"]:
        for key in ["id", "category", "name", "target_level", "description", "learning_goal",
                    "recommended_problem_levels", "related_tags"]:
            if key not in it:
                error(f"curriculum.yaml: {it.get('id')} に {key} がない")
        if it["id"] in items:
            error(f"curriculum.yaml: id 重複 {it['id']}")
        if it["target_level"] not in ("Write", "Read", "AI"):
            error(f"curriculum.yaml: {it['id']} の target_level が不正")
        if it["category"] not in cur["categories"]:
            error(f"curriculum.yaml: {it['id']} の category が不正")
        for t in it["related_tags"]:
            if t not in tags:
                error(f"curriculum.yaml: {it['id']} の related_tags {t} が tags.yaml にない")
        items[it["id"]] = it
    levels = Counter(it["target_level"] for it in items.values())
    print(f"tags: {len(tags)} / curriculum items: {len(items)} {dict(levels)}")
    return tags, items, cur["categories"]


# ---------------------------------------------------------------- metadata

def check_metadata(tags, items, categories):
    section("metadata")
    metas = {}
    for d in sorted(PROBLEMS.glob("P*")):
        meta = load_yaml(d / "metadata.yaml")
        pid = meta.get("id")
        for key in REQUIRED_META:
            if key not in meta:
                error(f"{d.name}: metadata に {key} がない")
        if pid != d.name:
            error(f"{d.name}: id({pid}) がディレクトリ名と違う")
        if pid in metas:
            error(f"{pid}: id が重複")
        if meta["problem_type"] not in ("coding", "exploration"):
            error(f"{pid}: problem_type が不正")
        if meta["category"] not in categories or meta["category"] == "X":
            error(f"{pid}: category が不正 {meta['category']}")
        if meta["difficulty"] not in (1, 2, 3) or meta["learning_level"] not in (1, 2, 3):
            error(f"{pid}: difficulty / learning_level は 1〜3")
        if not meta["primary_tags"]:
            error(f"{pid}: primary_tags が空")
        if len(meta["primary_tags"]) > 3:
            warn(f"{pid}: primary_tags が多すぎる({len(meta['primary_tags'])}個)")
        if set(meta["primary_tags"]) & set(meta["secondary_tags"]):
            error(f"{pid}: primary と secondary に同じタグ")
        for t in meta["primary_tags"] + meta["secondary_tags"]:
            if t not in tags:
                error(f"{pid}: タグ {t} が tags.yaml にない")
        for it in meta["curriculum_items"]:
            if it not in items:
                error(f"{pid}: curriculum_items {it} が curriculum.yaml にない")
            elif items[it]["target_level"] != "Write":
                warn(f"{pid}: Write 対象でない curriculum item {it}({items[it]['target_level']})を出題している")
        for f in meta.get("datasets") or []:
            if not (d / "data" / f).exists():
                error(f"{pid}: data/{f} がない")
        for f in ["exercise.ipynb", "solution.ipynb", "content.yaml"] + (["tests.py"] if meta["problem_type"] == "coding" else []):
            if not (d / f).exists():
                error(f"{pid}: {f} がない")
        metas[pid] = meta
    for pid, meta in metas.items():
        for ref in meta["prerequisites"] + ([meta["variant_of"]] if meta["variant_of"] else []):
            if ref not in metas:
                error(f"{pid}: 参照先 {ref} が存在しない")
    print(f"problems: {len(metas)}")
    return metas


# ---------------------------------------------------------------- 分布

def check_balance(metas):
    section("balance")
    n = len(metas)
    by_cat = Counter(m["category"] for m in metas.values())
    by_type = Counter(m["problem_type"] for m in metas.values())
    by_level = Counter(m["learning_level"] for m in metas.values())
    print("category:", dict(sorted(by_cat.items())))
    print("type:", dict(by_type), f"(exploration {by_type['exploration'] / n:.0%})")
    print("learning_level:", dict(sorted(by_level.items())))
    for cat, c in by_cat.items():
        if c / n > 0.35:
            warn(f"category {cat} に偏っている({c}/{n})")
    if not 0.1 <= by_type["exploration"] / n <= 0.3:
        warn(f"exploration の割合が目安(約20%)から外れている: {by_type['exploration']}/{n}")
    if by_level[2] < max(by_level[1], by_level[3]):
        warn("Level 2 が最多になっていない")


# ---------------------------------------------------------------- notebook と解答

def check_notebooks(metas):
    section("notebooks / solutions")
    n_pass = 0
    for pid, meta in metas.items():
        d = PROBLEMS / pid
        ex = nbformat.read(d / "exercise.ipynb", as_version=4)
        sol = nbformat.read(d / "solution.ipynb", as_version=4)
        for nb, name in [(ex, "exercise"), (sol, "solution")]:
            try:
                nbformat.validate(nb)
            except nbformat.ValidationError as e:
                error(f"{pid}: {name}.ipynb が不正 {e}")
            for src in code_cells(nb):
                for pattern, api in BANNED.items():
                    if re.search(pattern, src):
                        warn(f"{pid}: {name} のコードに Write 対象外の {api} がある")
        ex_src = "\n".join(code_cells(ex))
        if f'save_review("{pid}"' not in ex_src:
            error(f"{pid}: exercise に感想保存セルがない")
        sol_cells = code_cells(sol, "solution")
        if not sol_cells:
            error(f"{pid}: solution に tag=solution のセルがない")
            continue

        if meta["problem_type"] == "exploration":
            if f'done("{pid}")' not in ex_src:
                error(f"{pid}: exercise に done() セルがない")
            continue

        if f'check("{pid}", solve)' not in ex_src:
            error(f"{pid}: exercise に採点セルがない")
        body = [line.strip() for line in sol_cells[0].splitlines()[1:] if line.strip()]
        if any(line in ex_src for line in body if len(line) > 12):
            error(f"{pid}: exercise に模範解答のコードが含まれている")

        # 模範解答はすべてのテストを通る
        results = grader.run_tests(pid, _define_solve(sol_cells[0]))
        failed = [(c["name"], reason) for c, reason, _ in results if reason]
        if failed:
            error(f"{pid}: 模範解答がテストに失敗 {failed}")
        else:
            n_pass += 1
        if len(results) < 2:
            warn(f"{pid}: テストケースが {len(results)} 個しかない")

        # 解答欄のままでは1つもテストを通らない(テストが甘すぎないこと)
        stub = code_cells(ex, "answer")
        if stub:
            stub_results = grader.run_tests(pid, _define_solve(stub[0]))
            if any(reason is None for _, reason, _ in stub_results):
                error(f"{pid}: 空の解答欄でも通ってしまうテストがある")

        # 模範解答が実データでもエラーなく動く
        content = load_yaml(d / "content.yaml")
        try:
            with _chdir(d):
                ns = {"pd": pd}
                exec(content["setup"], ns)
                exec(sol_cells[0], ns)
                eval(content["run"], ns)
        except Exception as e:
            error(f"{pid}: 模範解答が実データで失敗 {type(e).__name__}: {e}")
    print(f"coding solutions passing all tests: {n_pass}/{sum(m['problem_type'] == 'coding' for m in metas.values())}")


def _define_solve(src):
    ns = {"pd": pd}
    exec(src, ns)
    return ns["solve"]


@contextlib.contextmanager
def _chdir(path):
    prev = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev)


@contextlib.contextmanager
def _temp_review_dir():
    prev = os.environ.get("PANDAS_PRACTICE_REVIEW_DIR")
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["PANDAS_PRACTICE_REVIEW_DIR"] = tmp
        try:
            yield Path(tmp)
        finally:
            if prev is None:
                os.environ.pop("PANDAS_PRACTICE_REVIEW_DIR", None)
            else:
                os.environ["PANDAS_PRACTICE_REVIEW_DIR"] = prev


# ---------------------------------------------------------------- 感想保存・履歴

def check_review_and_history():
    section("review / history")
    with _temp_review_dir() as tmp, contextlib.redirect_stdout(io.StringIO()) as out:
        review.save_review("P001", "groupbyが曖昧")
        review.save_review("P001", "")
        review.save_review("P001", "   \n  ")
        review.save_review("P001", "groupbyが曖昧")            # 直後の同一内容 -> 保存しない
        review.save_review("P002", '''
            isnaのあとmeanで割合になるの便利
            "引用符" や : を含んでも大丈夫
        ''')
        original_now = review.now
        review.now = lambda: original_now() + timedelta(minutes=6)
        try:
            review.save_review("P001", "groupbyが曖昧")        # 5分以上後 -> 保存する
        finally:
            review.now = original_now
        reviews = load_yaml(tmp / "notes.yaml")["reviews"]

        grader._hints_shown.clear()
        correct = _define_solve("def solve(df):\n    return df.shape")
        wrong = _define_solve("def solve(df):\n    return len(df)")
        grader.check("P002", correct)
        grader.check("P002", correct)                          # 直後の同一結果 -> 記録しない
        grader.check("P002", wrong)
        grader.hint("P003")
        grader.check("P003", _define_solve("def solve(df):\n    return df.columns"))
        grader.done("P006")
        grader.done("P006")
        history = pd.read_csv(tmp / "history.csv")

    printed = out.getvalue()
    expect = [
        (len(reviews) == 3, "notes.yaml に3件だけ追記される(空・直後の重複はスキップ)"),
        (reviews[1]["impression"] == 'isnaのあとmeanで割合になるの便利\n"引用符" や : を含んでも大丈夫', "複数行の感想が崩れずに保存される"),
        ("Saved review: P001" in printed, "保存時に Saved review と表示される"),
        (list(history.columns) == grader.HISTORY_COLUMNS, "history.csv の列"),
        (len(history) == 4, "history.csv に4行(重複採点はスキップ)"),
        (history["passed"].tolist() == [True, False, True, True], "passed の記録"),
        (history["hint_used"].tolist() == [False, False, True, False], "hint_used の記録"),
        (history["score"].tolist() == ["3/3", "0/3", "3/3", "exploration"], "score の記録"),
    ]
    for passed, label in expect:
        print(("OK   " if passed else "FAIL ") + label)
        if not passed:
            error(f"review/history: {label}")

    # 本物の review ファイルが読めること
    real = ROOT / "review"
    try:
        review.load_reviews()
        if (real / "history.csv").stat().st_size:
            pd.read_csv(real / "history.csv")
    except Exception as e:
        error(f"review/ のファイルが読めない: {e}")


# ---------------------------------------------------------------- Notebook の実行

def execute_notebooks(metas):
    section("execute notebooks")
    from nbclient import NotebookClient

    with _temp_review_dir():
        for pid in metas:
            d = PROBLEMS / pid
            for name in ["exercise.ipynb", "solution.ipynb"]:
                nb = nbformat.read(d / name, as_version=4)
                try:
                    NotebookClient(nb, timeout=120, kernel_name="python3", resources={"metadata": {"path": str(d)}}).execute()
                except Exception as e:
                    error(f"{pid}/{name} の実行に失敗: {str(e).splitlines()[0]}")
            print(f"{pid} ok", end="  ", flush=True)
    print()


def main():
    tags, items, categories = check_config()
    metas = check_metadata(tags, items, categories)
    check_balance(metas)
    check_notebooks(metas)
    check_review_and_history()
    if "--execute" in sys.argv:
        execute_notebooks(metas)

    section("result")
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"\n{len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
