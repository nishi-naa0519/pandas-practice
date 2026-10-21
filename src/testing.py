"""各問題の tests.py から使うヘルパーと、解答と期待値の比較ロジック。

tests.py は次の形で書く:

    from src.testing import case

    def make_cases():
        return [
            case("基本ケース", args={"df": ...}, expected=...),
            case("境界ケース", args={"df": ...}, expected=..., ignore_order=True),
        ]

比較オプション(case の追加キーワード引数):
    ignore_order   行(Series/DataFrame)や要素(list)の順番を無視する
    ignore_index   DataFrame/Series の index を無視する(reset_index して比較)
    as_set         list / Index / set を集合として比較する
    rtol           float の相対誤差(デフォルト 1e-6)

tests.py に `normalize(result)` を定義すると、比較前に解答へ適用される
(例: dtypes を文字列にそろえる)。
"""

import math

import numpy as np
import pandas as pd

DEFAULT_RTOL = 1e-6


def case(name, args, expected, **options):
    return {"name": name, "args": args, "expected": expected, "options": options}


def _type_name(obj):
    return "None" if obj is None else type(obj).__name__


def compare(got, expected, *, ignore_order=False, ignore_index=False, as_set=False, rtol=DEFAULT_RTOL):
    """一致すれば None、違えば理由の文字列を返す。"""
    if got is None and expected is not None:
        return "何も返されていません。`return` を忘れていませんか？"

    if isinstance(expected, pd.DataFrame):
        return _compare_frame(got, expected, ignore_order, ignore_index, rtol)
    if isinstance(expected, pd.Series):
        return _compare_series(got, expected, ignore_order, ignore_index, rtol)
    if as_set or isinstance(expected, set):
        return _compare_set(got, expected)
    if isinstance(expected, (list, tuple)):
        return _compare_sequence(got, expected, ignore_order, rtol)
    return _compare_scalar(got, expected, rtol)


def _compare_frame(got, expected, ignore_order, ignore_index, rtol):
    if not isinstance(got, pd.DataFrame):
        return f"DataFrame を返してください(実際: {_type_name(got)})"
    if list(got.columns) != list(expected.columns):
        return f"列が違います\n  期待: {list(expected.columns)}\n  実際: {list(got.columns)}"
    if got.shape != expected.shape:
        return f"形(shape)が違います  期待: {expected.shape} / 実際: {got.shape}"
    if ignore_index:
        got, expected = got.reset_index(drop=True), expected.reset_index(drop=True)
    if ignore_order:
        got, expected = _sort_rows(got), _sort_rows(expected)
    try:
        pd.testing.assert_frame_equal(
            got, expected,
            check_dtype=False, check_names=False, check_index_type=False,
            check_column_type=False, check_exact=False, rtol=rtol, check_freq=False,
        )
    except AssertionError as e:
        return "値または index が違います\n" + _short(e)
    return None


def _compare_series(got, expected, ignore_order, ignore_index, rtol):
    if not isinstance(got, pd.Series):
        return f"Series を返してください(実際: {_type_name(got)})"
    if len(got) != len(expected):
        return f"要素数が違います  期待: {len(expected)} / 実際: {len(got)}"
    if ignore_index:
        got, expected = got.reset_index(drop=True), expected.reset_index(drop=True)
    if ignore_order:
        got, expected = _sort_series(got), _sort_series(expected)
    try:
        pd.testing.assert_series_equal(
            got, expected,
            check_dtype=False, check_names=False, check_index_type=False,
            check_exact=False, rtol=rtol, check_freq=False,
        )
    except AssertionError as e:
        return "値または index が違います\n" + _short(e)
    return None


def _sort_rows(df):
    return df.sort_values(list(df.columns), kind="stable").reset_index(drop=True)


def _sort_series(s):
    return s.sort_index(kind="stable")


def _to_list(got):
    if isinstance(got, (pd.Index, np.ndarray)):
        return list(got)
    if isinstance(got, (list, tuple, set)):
        return list(got)
    return None


def _compare_set(got, expected):
    items = _to_list(got)
    if items is None:
        return f"集合(set)かリストを返してください(実際: {_type_name(got)})"
    if set(items) != set(expected):
        return f"値の集合が違います\n  期待: {sorted(map(str, expected))}\n  実際: {sorted(map(str, items))}"
    return None


def _compare_sequence(got, expected, ignore_order, rtol):
    items = _to_list(got)
    if items is None:
        return f"{type(expected).__name__} を返してください(実際: {_type_name(got)})"
    if len(items) != len(expected):
        return f"要素数が違います  期待: {len(expected)} / 実際: {len(items)}"
    if ignore_order:
        items, expected = sorted(items, key=str), sorted(expected, key=str)
    for i, (g, e) in enumerate(zip(items, expected)):
        reason = _compare_scalar(g, e, rtol)
        if reason:
            return f"{i}番目の要素が違います: {reason}"
    return None


def _compare_scalar(got, expected, rtol):
    if isinstance(expected, (bool, np.bool_)):
        if not isinstance(got, (bool, np.bool_)):
            return f"True/False を返してください(実際: {_type_name(got)} {got!r})"
        return None if bool(got) == bool(expected) else f"期待: {expected} / 実際: {got}"
    if isinstance(expected, (int, float, np.integer, np.floating)):
        if isinstance(got, (bool, np.bool_)) or not isinstance(got, (int, float, np.integer, np.floating)):
            return f"数値を返してください(実際: {_type_name(got)} {got!r})"
        if math.isnan(expected) and math.isnan(got):
            return None
        if math.isclose(float(got), float(expected), rel_tol=rtol, abs_tol=1e-9):
            return None
        return f"期待: {expected} / 実際: {got}"
    if got != expected:
        return f"期待: {expected!r} / 実際: {got!r}"
    return None


def _short(e, max_lines=12):
    # assert_*_equal は (got, expected) の順で呼んでいるので left = あなたの出力
    text = str(e).replace("[left]:", "[あなた]:").replace("[right]:", "[期待]:")
    lines = [line for line in text.strip().splitlines() if line.strip()]
    return "\n".join("  " + line for line in lines[:max_lines])
