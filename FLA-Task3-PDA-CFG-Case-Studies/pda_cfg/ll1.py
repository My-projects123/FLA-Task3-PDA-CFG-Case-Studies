"""
Small LL(1) predictive parser for the unambiguous arithmetic grammar
after left-recursion elimination:

  E  → T E'
  E' → + T E' | ε
  T  → F T'
  T' → * F T' | ε
  F  → ( E ) | id
"""

from __future__ import annotations

from typing import List, Optional, Tuple


class LL1ExpressionParser:
    def __init__(self):
        self.tokens: List[str] = []
        self.i = 0
        self.trace: List[str] = []

    def parse(self, tokens: List[str]) -> Tuple[bool, List[str]]:
        self.tokens = tokens + ["$"]
        self.i = 0
        self.trace = []
        try:
            self._E()
            ok = self._peek() == "$"
            return ok, self.trace
        except SyntaxError as exc:
            self.trace.append(f"error: {exc}")
            return False, self.trace

    def _peek(self) -> str:
        return self.tokens[self.i]

    def _match(self, tok: str) -> None:
        if self._peek() != tok:
            raise SyntaxError(f"expected {tok}, got {self._peek()}")
        self.trace.append(f"match {tok}")
        self.i += 1

    def _E(self) -> None:
        self.trace.append("E → T E'")
        self._T()
        self._Ep()

    def _Ep(self) -> None:
        if self._peek() == "+":
            self.trace.append("E' → + T E'")
            self._match("+")
            self._T()
            self._Ep()
        else:
            self.trace.append("E' → ε")

    def _T(self) -> None:
        self.trace.append("T → F T'")
        self._F()
        self._Tp()

    def _Tp(self) -> None:
        if self._peek() == "*":
            self.trace.append("T' → * F T'")
            self._match("*")
            self._F()
            self._Tp()
        else:
            self.trace.append("T' → ε")

    def _F(self) -> None:
        if self._peek() == "(":
            self.trace.append("F → ( E )")
            self._match("(")
            self._E()
            self._match(")")
        elif self._peek() == "id":
            self.trace.append("F → id")
            self._match("id")
        else:
            raise SyntaxError(f"factor expected, got {self._peek()}")


def tokenize_expr(text: str) -> Optional[List[str]]:
    """Tokenize a compact expression language: id, +, *, (, )."""
    tokens: List[str] = []
    i = 0
    while i < len(text):
        if text[i].isspace():
            i += 1
            continue
        if text.startswith("id", i):
            tokens.append("id")
            i += 2
            continue
        if text[i] in "+*()":
            tokens.append(text[i])
            i += 1
            continue
        return None
    return tokens
