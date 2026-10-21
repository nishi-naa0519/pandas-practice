# CLAUDE.md — pandas-practice

## このプロジェクトの目的

ユーザー(MLエンジニア)が、Jupyter Notebook でデータを探索するときに
「AIに頼むより自分で書いたほうが速い」程度の pandas 操作を、何も見ずに反射的に書けるようになるための学習システム。

最終ゴール: **初めて見るCSVを開き、構造・欠損・型・分布・カテゴリ・簡単なグループ差を数分で自力で確認できる。**

pandas を網羅的に学ぶことは目的ではない。複雑な処理はAIに書かせる前提。
機能の多さより「学習を始めるまでの摩擦が少ない」「Notebookだけで完結する」ことを優先する。

## Write / Read / AI

`config/curriculum.yaml` の `target_level` に従う。

- **Write**: 何も見ずに5〜10秒で書けるようにする。問題演習の中心
- **Read**: 読めればよい。暗記用の問題を作らない
- **AI**: AIに書かせればよい。問題を作らない

守ること:
- 出題は `curriculum.yaml` の Write 項目の範囲で行う。Read / AI 項目(MultiIndex, stack/unstack, melt, 複雑な pivot_table, rolling, expanding, resample, apply, transform, query, eval, xs, 長い method chaining など)を解答に要求しない
- 同じ目的のAPIを複数教えない。Write 項目の `basic_form` を使う(条件抽出は `df[df["a"] >= 20]`、上位N件は `sort_values().head()`、など)
- solution で Read / AI 対象の書き方を「こちらがスマート」と紹介しない。別解は原則なし、出すとしても1つ
- `apply()` は使わない。ベクトル演算や標準メソッドで書く
- シンプルで読みやすいコードを優先する(途中結果を変数に入れてよい)
- 問題文・exercise に最初からヒントや解答を書かない。ヒントは `content.yaml` の `hints` に書き、`hint("Pxxx")` で1つずつ出す

## ファイル構成と役割

```
config/curriculum.yaml   学習範囲(Write/Read/AI, basic_form)
config/tags.yaml         使用可能なタグの一覧
problems/Pxxx/
  metadata.yaml          問題のメタ情報(タグ・レベルなど)
  content.yaml           Notebook の元になる問題文・解答・解説・ヒント
  tests.py               採点ケース(coding のみ)
  exercise.ipynb         ユーザーが解く Notebook(ユーザーの解答が入っている)
  exercise_retry_*.ipynb 解き直し用の Notebook(ユーザーの解答が入っている)
  solution.ipynb         解答と解説(content.yaml から生成)
  data/                  問題用データ
review/notes.yaml        ユーザーの感想(自由記述)の履歴
review/history.csv       採点結果の履歴(problem_id, timestamp, passed, hint_used, score)
src/grader.py            check / hint / done と履歴記録
src/review.py            save_review(感想の追記)
src/testing.py           tests.py 用の case() と比較ロジック
tools/make_datasets.py   合成データの生成
tools/build_problems.py  content.yaml → Notebook の生成
tools/validate.py        全体の機械的チェック
```

## 絶対に守ること(ユーザーデータ)

- `exercise.ipynb` / `exercise_retry_*.ipynb` を変更・削除・再生成しない(ユーザーの解答が入っている)。`build_problems.py` は既存の exercise を上書きしない作りなので、それを回避するような操作をしない
- `review/notes.yaml` を書き換えない。追記は `save_review()` 経由でユーザーが行う
- `review/history.csv` を削除・リセット・編集しない
- 既存問題の `tests.py` / `content.yaml` を変更する場合は理由をユーザーに伝える(過去の履歴の意味が変わるため)

## タグ

- タグは `config/tags.yaml` に登録されたものだけ使う。自由に新しいタグ名を作らない
- 新しいタグが本当に必要なら、命名規則 `<method|syntax|task|concept>:<snake_case>` で tags.yaml に先に追加し、ユーザーに伝える
- `primary_tags`(1〜2個、多くても3個)は**その問題で本当に習得してほしいもの**。途中で使うだけのメソッドは `secondary_tags` に入れる
- 復習時に「groupby が主目的だった問題」を primary_tags で正しく抽出できるようにする

## 問題の追加手順

1. 新しいIDを決める(既存の最大ID + 1。`problems/` を確認する)
2. `problems/Pxxx/` に `metadata.yaml`, `content.yaml`, (coding なら)`tests.py` を作る。形式は既存の問題をコピーして合わせる
3. `uv run python tools/build_problems.py Pxxx` で data と Notebook を生成する
4. `uv run python tools/validate.py` を実行し、**0 errors** を確認する(模範解答が全テストを通ること、空の解答欄が通らないこと、タグの存在などを検証する)
5. 必要なら `uv run python tools/validate.py --execute` で Notebook を実際に実行して確認する

### metadata.yaml

```yaml
id: P048
title: ...
category: E               # curriculum.yaml の categories (A〜H)
problem_type: coding      # coding / exploration
difficulty: 2             # 1: 単一操作 / 2: 2〜3操作の組み合わせ / 3: 簡単な実務EDA
learning_level: 2         # 1: 単一操作 / 2: 小さな組み合わせ / 3: EDAタスク(関数を指定しない)
primary_tags: [method:groupby]
secondary_tags: [method:mean, task:group_comparison]
curriculum_items: [groupby_single]   # curriculum.yaml の id(Write 項目)
estimated_minutes: 3
prerequisites: [P023]
datasets: [orders.csv]
source_type: synthetic
variant_of: null          # 類題なら元問題のID
created: "2026-10-22"
```

### content.yaml

- coding: `purpose`, `statement`, `data`, `setup`(読み込みコード), `preview`(任意), `signature`, `run`(実データでの実行式), `hints`, `solution: {code, explanation, points, mistakes, alternative(任意)}`
- exploration: `purpose`, `statement`, `questions`, `data`, `setup`, `hints`, `solution: {checklist, code(セル区切りは "# %%"), observations, points}`
- exploration の `observations` には**実際のデータで確認した事実**を書く(数値は実際に計算して確かめる)

### tests.py

```python
import pandas as pd
from src.testing import case

def make_cases():
    return [
        case("基本ケース", {"df": pd.DataFrame(...)}, expected),
        case("境界ケース", {"df": ...}, expected, ignore_order=True),
    ]
```

- 引数の dict のキーは solve の引数名と同じ順番にする(位置引数で渡される)
- オプション: `ignore_order`, `ignore_index`, `as_set`, `rtol`。dtypes のように比較前に変換したいときは `normalize(result)` を定義する
- **期待値は手計算できる小さなデータで書く。模範解答の出力をそのまま期待値にしない**
- 基本ケース + 境界ケース(欠損あり・該当なし・同値・行数が少ない など)を2〜3個。複雑にしすぎない
- 順番が意味を持つ問題(ランキングなど)では、同値で順番が曖昧にならないデータにする
- よくある間違い(`>` と `>=`、`sum` と `mean`、`how="left"` 忘れ など)で落ちるケースを含める

### データ

- 合成データを基本とし、`tools/make_datasets.py` に関数を追加して `DATASETS` に登録する(シード固定)
- 実務を想像できるドメイン(EC、アプリ、Webログ、特徴量テーブル、売上、広告など)。`a`, `b`, `c` のような列名は tests.py の中だけにする
- 外部データに依存しない。巨大なファイルを置かない

## 復習問題の作成(「苦手なタグを中心に復習問題を5問作って」など)

**必ず次のファイルを読んでから判断する:**

1. `review/history.csv` — 問題ごとの正誤・回数・ヒント使用
2. `review/notes.yaml` — ユーザーの感想
3. 各問題の `metadata.yaml` — primary_tags / curriculum_items / variant_of
4. `config/tags.yaml`, `config/curriculum.yaml` — 使えるタグと Write 範囲

**優先度を上げるもの:**
- `passed=false` の記録がある(特に最後の記録が false)
- 感想に「曖昧」「わからなかった」「忘れた」「復習したい」「迷った」などがある
- 正解しているが、何度も失敗してから正解した / `hint_used=true` で正解した
- 長期間解いていない基本操作

**優先度を下げるもの:**
- 継続的に一発で正解している
- 感想に「余裕」「慣れた」「すぐ書けた」などがある

複雑なスコアリングは不要。ファイルを読んで合理的に判断し、**なぜその問題を選んだか(根拠となる履歴・感想)をユーザーに短く説明する。**

### モード

- **A. 同じ問題を解き直す**: 新しい問題は作らない。`uv run python tools/build_problems.py --retry P012 P015` で解き直し用の空の Notebook を作り、どれを解けばよいか伝える
- **B. タグ指定の類題**(例: 「groupbyを中心に3問」): 苦手な既存問題を参考に新しい問題を作る。`primary_tags` に指定タグを入れ、`variant_of` に元問題IDを書く
- **C. 複合EDA問題**: 習得済みの基本操作を組み合わせた Level 3 の問題(exploration、または関数を指定しない coding)を作る

### 類題のルール

- 列名や数値を変えただけの実質同一問題を作らない
- 最低でも次のどれかを変える: データのドメイン / 問い方 / 組み合わせる操作 / 境界条件 / 問題の文脈 / 出力形式
  - 例: 元「各列の欠損数」→ 類題「各列の欠損率を高い順に」「欠損率が30%を超える列名のリスト」「欠損がある行のうち特定の店舗の割合」
- 類題でも Write 範囲を超えない。難しさは「簡単なAPIの組み合わせ方」で作る
- 作成後は必ず validate を実行し、0 errors を確認してから報告する
