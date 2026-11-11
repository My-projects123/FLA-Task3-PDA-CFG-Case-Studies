"""
Context-free grammar utilities: leftmost derivations and parse-tree counting.

Ambiguity of CFGs is undecidable in general, so we count trees for every
string up to a bound and report collisions.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Set, Tuple


@dataclass(frozen=True)
class Production:
    lhs: str
    rhs: Tuple[str, ...]

    def __str__(self) -> str:
        body = " ".join(self.rhs) if self.rhs else "ε"
        return f"{self.lhs} → {body}"


class CFG:
    def __init__(
        self,
        name: str,
        start: str,
        productions: Iterable[Production],
        terminals: Iterable[str],
    ):
        self.name = name
        self.start = start
        self.productions = list(productions)
        self.terminals = set(terminals)
        self.nonterminals: Set[str] = {p.lhs for p in self.productions}
        self.by_lhs: Dict[str, List[Production]] = defaultdict(list)
        for p in self.productions:
            self.by_lhs[p.lhs].append(p)

    @classmethod
    def from_rules(
        cls,
        name: str,
        start: str,
        rules: Sequence[Tuple[str, Sequence[str]]],
        terminals: Iterable[str],
    ) -> "CFG":
        prods = [Production(lhs, tuple(rhs)) for lhs, rhs in rules]
        return cls(name, start, prods, terminals)

    def leftmost_derivations(self, tokens: Sequence[str], limit: int = 50) -> List[List[str]]:
        """Return up to `limit` leftmost derivation traces."""
        target = tuple(tokens)
        found: List[List[str]] = []
        todo = deque([([self.start], (self.start,))])

        while todo and len(found) < limit:
            steps, form = todo.popleft()
            idx = next((i for i, x in enumerate(form) if x in self.nonterminals), None)
            if idx is None:
                if form == target:
                    found.append(steps + [" ".join(form)])
                continue
            prefix = form[:idx]
            if prefix != target[: len(prefix)]:
                continue
            if len(form) > len(target) + 6:
                continue
            for prod in self.by_lhs[form[idx]]:
                new_form = form[:idx] + prod.rhs + form[idx + 1 :]
                if sum(1 for x in new_form if x in self.terminals) > len(target):
                    continue
                step = f"{' '.join(form)}  ⇒  {' '.join(new_form) or 'ε'}  ({prod})"
                todo.append((steps + [step], new_form))
        return found

    def count_parse_trees(self, tokens: Sequence[str]) -> int:
        """
        Count parse trees for `tokens`.

        Left recursion is handled by requiring every recursive nonterminal
        occurrence to consume a non-empty span ( Hopcroft-style progressive
        derivation on a finite string ).
        """
        n = len(tokens)
        memo: Dict[Tuple[str, int, int], int] = {}

        def ways(nt: str, i: int, j: int) -> int:
            key = (nt, i, j)
            if key in memo:
                return memo[key]
            total = 0
            for prod in self.by_lhs[nt]:
                total += match_rhs(prod.rhs, i, j, parent=nt)
            memo[key] = total
            return total

        def match_rhs(rhs: Tuple[str, ...], i: int, j: int, parent: str) -> int:
            if not rhs:
                return 1 if i == j else 0

            def rec(k: int, pos: int) -> int:
                if k == len(rhs):
                    return 1 if pos == j else 0
                sym = rhs[k]
                if sym in self.terminals:
                    if pos < j and tokens[pos] == sym:
                        return rec(k + 1, pos + 1)
                    return 0
                # Nonterminal: choose a split. Left-recursive A → A α must give the
                # first A a strictly shorter span than [pos, j), otherwise
                # ways(A,pos,j) re-enters itself forever.
                total = 0
                left_rec = k == 0 and sym == parent
                lo = pos + 1 if left_rec else pos
                hi = j if left_rec else j + 1  # left_rec: end in [lo, j)
                for end in range(lo, hi):
                    w = ways(sym, pos, end)
                    if w:
                        total += w * rec(k + 1, end)
                return total

            return rec(0, i)

        return ways(self.start, 0, n)

    def generate(self, max_len: int) -> Set[Tuple[str, ...]]:
        """All terminal strings of length ≤ max_len obtainable without runaway growth."""
        results: Set[Tuple[str, ...]] = set()
        todo = deque([(self.start,)])
        seen = {(self.start,)}
        while todo:
            form = todo.popleft()
            if all(x in self.terminals for x in form):
                if len(form) <= max_len:
                    results.add(form)
                continue
            if len(form) > max_len + 2:
                continue
            idx = next(i for i, x in enumerate(form) if x in self.nonterminals)
            for prod in self.by_lhs[form[idx]]:
                new_form = form[:idx] + prod.rhs + form[idx + 1 :]
                if len(new_form) <= max_len + 2 and new_form not in seen:
                    seen.add(new_form)
                    todo.append(new_form)
        return results
