"""Tests for Task 3 CFG/PDA case studies."""

import itertools

from pda_cfg.cases import (
    BRACKETS_AMBIGUOUS,
    BRACKETS_PDA,
    BRACKETS_REVISED,
    EXPR_AMBIGUOUS,
    EXPR_LL1,
    EXPR_NPDA,
    EXPR_PRECEDENCE,
    LL1_PARSER,
    PAL_WCWR_PDA,
    PAL_WWR_PDA,
    SAMPLES,
    bracket_tokens,
    oracle_brackets,
    oracle_wcwr,
    oracle_wwr,
)
from pda_cfg.ll1 import tokenize_expr


def test_brackets_samples():
    assert BRACKETS_PDA.is_deterministic()
    for s in SAMPLES["brackets"]["accept"]:
        assert BRACKETS_PDA.accepts(list(s))
        assert oracle_brackets(s)
    for s in SAMPLES["brackets"]["reject"]:
        assert not BRACKETS_PDA.accepts(list(s))
        assert not oracle_brackets(s)


def test_brackets_ambiguity_fixed():
    s = list("()()()")
    assert BRACKETS_AMBIGUOUS.count_parse_trees(s) >= 2
    assert BRACKETS_REVISED.count_parse_trees(s) == 1


def test_brackets_lexer():
    src = 'if (a[i] > 0) { sum += f(a[i]); }'
    toks = bracket_tokens(src)
    assert BRACKETS_PDA.accepts(toks)
    bad = "x = (a + b];"
    assert not BRACKETS_PDA.accepts(bracket_tokens(bad))


def test_brackets_exhaustive_short():
    alphabet = list("()[]")
    for n in range(0, 5):
        for chars in itertools.product(alphabet, repeat=n):
            s = "".join(chars)
            assert BRACKETS_PDA.accepts(list(s)) == oracle_brackets(s)


def test_expr_samples():
    for s in SAMPLES["expr"]["accept"]:
        toks = tokenize_expr(s)
        assert toks is not None
        assert LL1_PARSER.parse(toks)[0]
        assert EXPR_PRECEDENCE.count_parse_trees(toks) == 1
    for s in SAMPLES["expr"]["reject"]:
        toks = tokenize_expr(s)
        if toks is None:
            continue
        assert not LL1_PARSER.parse(toks)[0]


def test_expr_ambiguity():
    toks = ["id", "+", "id", "*", "id"]
    assert EXPR_AMBIGUOUS.count_parse_trees(toks) == 2
    assert EXPR_PRECEDENCE.count_parse_trees(toks) == 1
    assert EXPR_LL1.count_parse_trees(toks) == 1


def test_expr_npda_accepts():
    toks = ["id", "+", "id", "*", "id"]
    assert EXPR_NPDA.accepts(toks)


def test_wcwr_samples():
    assert PAL_WCWR_PDA.is_deterministic()
    for s in SAMPLES["wcwr"]["accept"]:
        assert PAL_WCWR_PDA.accepts(list(s))
        assert oracle_wcwr(s)
    for s in SAMPLES["wcwr"]["reject"]:
        assert not PAL_WCWR_PDA.accepts(list(s))
        assert not oracle_wcwr(s)


def test_wwr_samples():
    assert not PAL_WWR_PDA.is_deterministic()
    for s in SAMPLES["wwr"]["accept"]:
        assert PAL_WWR_PDA.accepts(list(s)), s
        assert oracle_wwr(s)
    for s in SAMPLES["wwr"]["reject"]:
        assert not PAL_WWR_PDA.accepts(list(s)), s
        assert not oracle_wwr(s)
