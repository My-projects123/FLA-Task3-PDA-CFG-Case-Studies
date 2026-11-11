"""CLI demo for Task 3 CFG/PDA case studies."""

from __future__ import annotations

import argparse

from .cases import (
    BRACKETS_AMBIGUOUS,
    BRACKETS_PDA,
    BRACKETS_REVISED,
    EXPR_AMBIGUOUS,
    EXPR_LL1,
    EXPR_NPDA,
    EXPR_PRECEDENCE,
    LL1_PARSER,
    PAL_CENTERED_CFG,
    PAL_CFG,
    PAL_WCWR_PDA,
    PAL_WWR_PDA,
    SAMPLES,
    bracket_tokens,
    oracle_brackets,
    oracle_wcwr,
    oracle_wwr,
)
from .ll1 import tokenize_expr


def _show_brackets() -> None:
    print("\n=== Case 1: Balanced brackets ===")
    print(f"DPDA deterministic? {BRACKETS_PDA.is_deterministic()}")
    print("Ambiguous grammar trees for ()()():", BRACKETS_AMBIGUOUS.count_parse_trees(list("()()()")))
    print("Revised grammar trees for ()()():", BRACKETS_REVISED.count_parse_trees(list("()()()")))
    for s in SAMPLES["brackets"]["accept"]:
        ok, path, _ = BRACKETS_PDA.run(list(s))
        print(f"  ACCEPT? {ok}  {s}")
        if ok and s == "{[()]}":
            print("    " + " ⊢ ".join(path))
    for s in SAMPLES["brackets"]["reject"]:
        ok, _, _ = BRACKETS_PDA.run(list(s))
        print(f"  REJECT? {not ok}  {s}")
    src = 'if (a[i] > 0) { sum += f(a[i]); }'
    toks = bracket_tokens(src)
    print(f"  lexer {src!r} -> {''.join(toks)} -> {BRACKETS_PDA.accepts(toks)}")


def _show_expr() -> None:
    print("\n=== Case 2: Arithmetic expressions ===")
    tokens = ["id", "+", "id", "*", "id"]
    print("Ambiguous trees for id+id*id:", EXPR_AMBIGUOUS.count_parse_trees(tokens))
    print("Precedence trees for id+id*id:", EXPR_PRECEDENCE.count_parse_trees(tokens))
    print("LL(1) trees for id+id*id:", EXPR_LL1.count_parse_trees(tokens))
    print("Leftmost derivations (ambiguous):")
    for d in EXPR_AMBIGUOUS.leftmost_derivations(tokens, limit=2):
        print("  --")
        for line in d[:8]:
            print("   ", line)
    ok, path, explored = EXPR_NPDA.run(tokens)
    print(f"CFG→NPDA accepts id+id*id? {ok} (explored {explored} configs)")
    tok = tokenize_expr("id+id*id")
    ok, trace = LL1_PARSER.parse(tok)
    print(f"LL(1) parse ok? {ok}")
    for line in trace[:12]:
        print("   ", line)
    for s in SAMPLES["expr"]["accept"]:
        t = tokenize_expr(s)
        print(f"  ACCEPT {s}: CFG-trees={EXPR_PRECEDENCE.count_parse_trees(t)} LL1={LL1_PARSER.parse(t)[0]}")
    for s in SAMPLES["expr"]["reject"]:
        t = tokenize_expr(s)
        if t is None:
            print(f"  REJECT {s}: tokenize failed")
        else:
            print(f"  REJECT {s}: LL1={LL1_PARSER.parse(t)[0]}")


def _show_palindrome() -> None:
    print("\n=== Case 3: Palindromes ===")
    print(f"w c wR DPDA deterministic? {PAL_WCWR_PDA.is_deterministic()}")
    print(f"w wR NPDA deterministic? {PAL_WWR_PDA.is_deterministic()}")
    ok, path, _ = PAL_WCWR_PDA.run(list("abcba"))
    print("abcba:", " ⊢ ".join(path) if ok else "reject")
    for s in SAMPLES["wcwr"]["accept"]:
        assert PAL_WCWR_PDA.accepts(list(s)) == oracle_wcwr(s)
        print(f"  wcwr ACCEPT {s}")
    for s in SAMPLES["wcwr"]["reject"]:
        print(f"  wcwr REJECT {s} -> {not PAL_WCWR_PDA.accepts(list(s))}")
    for s in SAMPLES["wwr"]["accept"]:
        print(f"  wwr ACCEPT {s!r} -> {PAL_WWR_PDA.accepts(list(s))}")
    for s in SAMPLES["wwr"]["reject"]:
        print(f"  wwr REJECT {s!r} -> {not PAL_WWR_PDA.accepts(list(s))}")


def _ambiguity() -> None:
    print("\n=== Bounded ambiguity check ===")
    checks = [
        ("brackets ambiguous", BRACKETS_AMBIGUOUS, 4),
        ("brackets revised", BRACKETS_REVISED, 4),
        ("expr ambiguous", EXPR_AMBIGUOUS, 3),
        ("expr precedence", EXPR_PRECEDENCE, 3),
        ("palindrome", PAL_CFG, 4),
        ("w c wR", PAL_CENTERED_CFG, 4),
    ]
    for name, cfg, maxlen in checks:
        multi = 0
        total = 0
        for form in cfg.generate(maxlen):
            # map terminals already
            tokens = list(form)
            if cfg is EXPR_AMBIGUOUS or cfg is EXPR_PRECEDENCE:
                # forms are tuples of symbols already token-like
                pass
            trees = cfg.count_parse_trees(tokens)
            total += 1
            if trees > 1:
                multi += 1
        print(f"  {name}: strings≤{maxlen}={total}, with ≥2 trees={multi}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="FLA Task 3 PDA/CFG demos")
    parser.add_argument(
        "cmd",
        nargs="?",
        default="all",
        choices=["all", "brackets", "expr", "palindrome", "ambiguity"],
    )
    args = parser.parse_args(argv)
    if args.cmd in ("all", "brackets"):
        _show_brackets()
    if args.cmd in ("all", "expr"):
        _show_expr()
    if args.cmd in ("all", "palindrome"):
        _show_palindrome()
    if args.cmd in ("all", "ambiguity"):
        _ambiguity()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
