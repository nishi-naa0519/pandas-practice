"""problems/Pxxx/content.yaml から Notebook とデータを生成する。

    uv run python tools/build_problems.py            # 全問題
    uv run python tools/build_problems.py P046 P047  # 指定した問題だけ
    uv run python tools/build_problems.py --retry P012  # 解き直し用の空の Notebook を追加で作る

- data/      : content.yaml の `data:` に書いたCSVを tools/make_datasets.py から生成(既存なら触らない)
- solution.ipynb : 毎回作り直す(ユーザーが編集するファイルではない)
- exercise.ipynb : 存在しない場合だけ作る。ユーザーの解答を守るため、既存ファイルは絶対に上書きしない
"""

import sys
from datetime import date
from pathlib import Path

import nbformat
import yaml
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import make_datasets  # noqa: E402

IMPORTS = "import pandas as pd\nfrom src.grader import check, hint"


def load(problem_dir):
    content = yaml.safe_load((problem_dir / "content.yaml").read_text(encoding="utf-8"))
    meta = yaml.safe_load((problem_dir / "metadata.yaml").read_text(encoding="utf-8"))
    return content, meta


def header(meta):
    kind = "コーディング" if meta["problem_type"] == "coding" else "探索(EDA)"
    return (
        f"# {meta['id']}: {meta['title']}\n\n"
        f"Level {meta['learning_level']} ・ {kind} ・ 目安 {meta['estimated_minutes']} 分"
    )


def review_cell(pid):
    return new_code_cell(
        "from src.review import save_review\n\n"
        "# 感想を一言。空のままなら保存されません(複数行は \"\"\"...\"\"\" でもOK)\n"
        'memo = ""\n\n'
        f'save_review("{pid}", memo)'
    )


def tagged(cell, tag):
    cell.metadata["tags"] = [tag]
    return cell


def exercise_notebook(c, meta):
    pid = meta["id"]
    cells = [
        new_markdown_cell(header(meta)),
        new_markdown_cell("## 目的\n\n" + c["purpose"].strip()),
        new_markdown_cell("## 問題\n\n" + c["statement"].strip()),
    ]
    if meta["problem_type"] == "coding":
        cells.append(new_code_cell(IMPORTS + "\n\n" + c["setup"].strip()))
        if c.get("preview"):
            cells.append(new_code_cell(c["preview"].strip()))
        cells += [
            new_markdown_cell(
                "## 解答\n\n`solve` の中を書いてください。"
                f"詰まったら別のセルで `hint(\"{pid}\")` を実行すると、ヒントが1つずつ表示されます。"
            ),
            tagged(new_code_cell(c["signature"].strip() + "\n    # ここに解答を書く\n    pass"), "answer"),
            new_markdown_cell("実データで結果を見てみる"),
            new_code_cell(c["run"].strip()),
            new_markdown_cell("## 採点"),
            new_code_cell(f'check("{pid}", solve)'),
        ]
    else:
        cells += [
            new_markdown_cell("### 調べ終わったら答えられるようにしたいこと\n\n" + c["questions"].strip()),
            new_code_cell("import pandas as pd\nfrom src.grader import done, hint\n\n" + c["setup"].strip()),
            new_markdown_cell(
                "## 探索\n\nセルは自由に追加してください。"
                f"何から見ればいいか迷ったら `hint(\"{pid}\")`。"
            ),
            new_code_cell(""),
            new_code_cell(""),
            new_code_cell(""),
            new_markdown_cell("## 完了を記録\n\n調べ終わったら実行してください。その後 `solution.ipynb` の確認項目と見比べましょう。"),
            new_code_cell(f'done("{pid}")'),
        ]
    cells += [new_markdown_cell("## 感想メモ"), review_cell(pid)]
    return new_notebook(cells=cells, metadata=NB_METADATA)


def solution_notebook(c, meta):
    pid = meta["id"]
    s = c["solution"]
    cells = [new_markdown_cell(header(meta) + "\n\n**解答と解説**")]
    if meta["problem_type"] == "coding":
        cells += [
            new_code_cell(IMPORTS + "\n\n" + c["setup"].strip()),
            new_markdown_cell("## 1. 模範解答"),
            tagged(new_code_cell(s["code"].strip()), "solution"),
            new_code_cell(c["run"].strip()),
            new_code_cell(f'check("{pid}", solve, record=False)  # 解答例の確認用(履歴には記録しない)'),
            new_markdown_cell("## 2. コードの説明\n\n" + s["explanation"].strip()),
            new_markdown_cell("## 3. 今回覚えるポイント\n\n" + s["points"].strip()),
            new_markdown_cell("## 4. よくある間違い\n\n" + s["mistakes"].strip()),
        ]
        if s.get("alternative"):
            cells.append(new_markdown_cell("## 5. 別解\n\n" + s["alternative"].strip()))
    else:
        cells += [
            new_code_cell("import pandas as pd\n\n" + c["setup"].strip()),
            new_markdown_cell("## 1. 推奨確認項目\n\n" + s["checklist"].strip()),
            new_markdown_cell("## 2. 模範的なコード"),
        ]
        for block in s["code"].split("# %%"):
            if block.strip():
                cells.append(tagged(new_code_cell(block.strip()), "solution"))
        cells += [
            new_markdown_cell("## 3. このデータで観察すべきポイント\n\n" + s["observations"].strip()),
            new_markdown_cell("## 4. 今回覚えるポイント\n\n" + s["points"].strip()),
        ]
    return new_notebook(cells=cells, metadata=NB_METADATA)


NB_METADATA = {
    "kernelspec": {"display_name": "Python 3 (ipykernel)", "language": "python", "name": "python3"},
    "language_info": {"name": "python"},
}


def build(problem_dir):
    c, meta = load(problem_dir)
    for name in c.get("data") or []:
        if not (problem_dir / "data" / name).exists():
            make_datasets.write(name, problem_dir / "data")

    nbformat.write(solution_notebook(c, meta), problem_dir / "solution.ipynb")
    exercise = problem_dir / "exercise.ipynb"
    if exercise.exists():
        return "solution updated (exercise kept)"
    nbformat.write(exercise_notebook(c, meta), exercise)
    return "created"


def build_retry(problem_dir):
    """解き直し用に、空の解答欄の Notebook を exercise_retry_YYYYMMDD.ipynb として作る(既存の解答は残す)。"""
    c, meta = load(problem_dir)
    stem = f"exercise_retry_{date.today():%Y%m%d}"
    path, n = problem_dir / f"{stem}.ipynb", 2
    while path.exists():
        path, n = problem_dir / f"{stem}_{n}.ipynb", n + 1
    nbformat.write(exercise_notebook(c, meta), path)
    return f"created {path.name}"


def main(args):
    retry = "--retry" in args
    ids = [a for a in args if not a.startswith("--")]
    if retry and not ids:
        sys.exit("--retry には問題IDを指定してください 例: --retry P012 P015")
    dirs = [ROOT / "problems" / i for i in ids] if ids else sorted((ROOT / "problems").glob("P*"))
    for d in dirs:
        print(f"{d.name}: {build_retry(d) if retry else build(d)}")


if __name__ == "__main__":
    main(sys.argv[1:])
