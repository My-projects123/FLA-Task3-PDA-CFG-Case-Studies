"""
Three case studies: balanced brackets, arithmetic expressions, palindromes.
"""

from __future__ import annotations

import re
from typing import List, Tuple

from .grammar import CFG
from .ll1 import LL1ExpressionParser, tokenize_expr
from .pda import EPS, Z0, PDA, Transition, cfg_to_npda

# ---------------------------------------------------------------------------
# 1. Balanced brackets
# ---------------------------------------------------------------------------

BRACKETS_AMBIGUOUS = CFG.from_rules(
    "brackets (ambiguous)",
    "S",
    [
        ("S", ("S", "S")),
        ("S", ("(", "S", ")")),
        ("S", ("[", "S", "]")),
        ("S", ("{", "S", "}")),
        ("S", ("(", ")")),
        ("S", ("[", "]")),
        ("S", ("{", "}")),
    ],
    terminals=list("()[]{}"),
)

BRACKETS_REVISED = CFG.from_rules(
    "brackets (unambiguous)",
    "S",
    [
        ("S", ("B", "S")),
        ("S", ("B",)),
        ("B", ("(", "S", ")")),
        ("B", ("(", ")")),
        ("B", ("[", "S", "]")),
        ("B", ("[", "]")),
        ("B", ("{", "S", "}")),
        ("B", ("{", "}")),
    ],
    terminals=list("()[]{}"),
)


def brackets_pda() -> PDA:
    """
    DPDA for non-empty balanced bracket strings (accept by final state).

    q1 is accepting only when the input is consumed and the stack is again
    exactly Z0. There is no ε-move, so openers on Z0 never race an ε-transition
    and the machine stays deterministic.
    """
    match = {")": "(", "]": "[", "}": "{"}
    trans = []
    for opener in "([{":
        trans.append(Transition("q0", opener, Z0, "q1", (Z0, opener)))
        trans.append(Transition("q1", opener, Z0, "q1", (Z0, opener)))
        for top in "([{":
            trans.append(Transition("q1", opener, top, "q1", (top, opener)))
    for closer, opener in match.items():
        trans.append(Transition("q1", closer, opener, "q1", tuple()))
    return PDA(
        name="Balanced brackets DPDA",
        states=["q0", "q1"],
        input_alphabet=list("()[]{}"),
        stack_alphabet=["Z0", "(", "[", "{"],
        transitions=trans,
        start="q0",
        accept_states={"q1"},
        require_bottom_stack=True,
    )


BRACKETS_PDA = brackets_pda()


def bracket_tokens(source: str) -> List[str]:
    """Lexer: keep brackets, skip string/char literals."""
    out: List[str] = []
    i = 0
    while i < len(source):
        ch = source[i]
        if ch in "\"'":
            quote = ch
            i += 1
            while i < len(source) and source[i] != quote:
                if source[i] == "\\" and i + 1 < len(source):
                    i += 2
                else:
                    i += 1
            i += 1
            continue
        if ch in "()[]{}":
            out.append(ch)
        i += 1
    return out


def oracle_brackets(s: str) -> bool:
    """Non-empty balanced bracket strings (matches the DPDA)."""
    if not s:
        return False
    stack = []
    match = {")": "(", "]": "[", "}": "{"}
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack[-1] != match[ch]:
                return False
            stack.pop()
        else:
            return False
    return not stack


# ---------------------------------------------------------------------------
# 2. Arithmetic expressions
# ---------------------------------------------------------------------------

EXPR_AMBIGUOUS = CFG.from_rules(
    "expr (ambiguous)",
    "E",
    [
        ("E", ("E", "+", "E")),
        ("E", ("E", "*", "E")),
        ("E", ("(", "E", ")")),
        ("E", ("id",)),
    ],
    terminals=["id", "+", "*", "(", ")"],
)

EXPR_PRECEDENCE = CFG.from_rules(
    "expr (precedence)",
    "E",
    [
        ("E", ("E", "+", "T")),
        ("E", ("T",)),
        ("T", ("T", "*", "F")),
        ("T", ("F",)),
        ("F", ("(", "E", ")")),
        ("F", ("id",)),
    ],
    terminals=["id", "+", "*", "(", ")"],
)

EXPR_LL1 = CFG.from_rules(
    "expr (LL(1))",
    "E",
    [
        ("E", ("T", "E'")),
        ("E'", ("+", "T", "E'")),
        ("E'", tuple()),
        ("T", ("F", "T'")),
        ("T'", ("*", "F", "T'")),
        ("T'", tuple()),
        ("F", ("(", "E", ")")),
        ("F", ("id",)),
    ],
    terminals=["id", "+", "*", "(", ")"],
)

# Use the non-left-recursive LL(1) grammar for the CFG→PDA construction so the
# NPDA does not loop on E → E + T. Precedence grammar is kept for tree counts.
EXPR_NPDA = cfg_to_npda(EXPR_LL1)
LL1_PARSER = LL1ExpressionParser()


def oracle_expr(tokens: List[str]) -> bool:
    ok, _ = LL1_PARSER.parse(tokens)
    return ok


# ---------------------------------------------------------------------------
# 3. Palindromes
# ---------------------------------------------------------------------------

PAL_CFG = CFG.from_rules(
    "palindrome over {a,b}",
    "S",
    [
        ("S", ("a", "S", "a")),
        ("S", ("b", "S", "b")),
        ("S", ("a",)),
        ("S", ("b",)),
        ("S", tuple()),
    ],
    terminals=["a", "b"],
)

PAL_CENTERED_CFG = CFG.from_rules(
    "w c wR",
    "S",
    [
        ("S", ("a", "S", "a")),
        ("S", ("b", "S", "b")),
        ("S", ("c",)),
    ],
    terminals=["a", "b", "c"],
)


def palindrome_wcwr_pda() -> PDA:
    """DPDA for { w c wR | w ∈ {a,b}* }."""
    trans = [
        Transition("q0", "a", Z0, "q0", (Z0, "a")),
        Transition("q0", "b", Z0, "q0", (Z0, "b")),
        Transition("q0", "a", "a", "q0", ("a", "a")),
        Transition("q0", "a", "b", "q0", ("b", "a")),
        Transition("q0", "b", "a", "q0", ("a", "b")),
        Transition("q0", "b", "b", "q0", ("b", "b")),
        Transition("q0", "c", Z0, "q1", (Z0,)),
        Transition("q0", "c", "a", "q1", ("a",)),
        Transition("q0", "c", "b", "q1", ("b",)),
        Transition("q1", "a", "a", "q1", tuple()),
        Transition("q1", "b", "b", "q1", tuple()),
        Transition("q1", EPS, Z0, "q2", (Z0,)),
    ]
    return PDA(
        name="DPDA for w c wR",
        states=["q0", "q1", "q2"],
        input_alphabet=["a", "b", "c"],
        stack_alphabet=[Z0, "a", "b"],
        transitions=trans,
        start="q0",
        accept_states={"q2"},
    )


def palindrome_wwr_pda() -> PDA:
    """NPDA for { w wR }: ε-guess the centre."""
    trans = [
        Transition("q0", "a", Z0, "q0", (Z0, "a")),
        Transition("q0", "b", Z0, "q0", (Z0, "b")),
        Transition("q0", "a", "a", "q0", ("a", "a")),
        Transition("q0", "a", "b", "q0", ("b", "a")),
        Transition("q0", "b", "a", "q0", ("a", "b")),
        Transition("q0", "b", "b", "q0", ("b", "b")),
        # guess centre
        Transition("q0", EPS, Z0, "q1", (Z0,)),
        Transition("q0", EPS, "a", "q1", ("a",)),
        Transition("q0", EPS, "b", "q1", ("b",)),
        Transition("q1", "a", "a", "q1", tuple()),
        Transition("q1", "b", "b", "q1", tuple()),
        Transition("q1", EPS, Z0, "q2", (Z0,)),
    ]
    return PDA(
        name="NPDA for w wR",
        states=["q0", "q1", "q2"],
        input_alphabet=["a", "b"],
        stack_alphabet=[Z0, "a", "b"],
        transitions=trans,
        start="q0",
        accept_states={"q2"},
    )


PAL_WCWR_PDA = palindrome_wcwr_pda()
PAL_WWR_PDA = palindrome_wwr_pda()


def oracle_wcwr(s: str) -> bool:
    if "c" not in s:
        return False
    i = s.index("c")
    if s.count("c") != 1:
        return False
    w, wr = s[:i], s[i + 1 :]
    return set(w) <= set("ab") and wr == w[::-1]


def oracle_wwr(s: str) -> bool:
    """Even-length palindromes { w wR | w ∈ {a,b}* } (centre is between letters)."""
    if any(ch not in "ab" for ch in s):
        return False
    return len(s) % 2 == 0 and s == s[::-1]


SAMPLES = {
    "brackets": {
        "accept": ["()", "[]{}", "([]{})", "{[()()]}", "((()))", "()[]{}([])"],
        "reject": ["(", ")(", "([)]", "(()", "{]}", "())(()"],
    },
    "expr": {
        "accept": ["id", "id+id*id", "(id+id)*id", "id*(id+id)*id", "((id))", "id+id+id"],
        "reject": ["", "id+", "+id", "id id", "(id+id", "id*)id(", "id+*id"],
    },
    "wcwr": {
        "accept": ["c", "aca", "abcba", "abbcbba", "babcbab", "aabacabaa"],
        "reject": ["", "ab", "abcab", "abcb", "acca", "abcbaa"],
    },
    "wwr": {
        "accept": ["", "aa", "abba", "baab", "abbbba", "aabbaabbaa"],
        "reject": ["a", "ab", "aba", "abab", "aabb", "abbaa"],
    },
}
