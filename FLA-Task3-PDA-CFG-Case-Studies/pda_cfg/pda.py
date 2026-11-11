"""
Pushdown automaton simulator over instantaneous descriptions (q, w, γ).

Supports acceptance by final state and/or empty stack, determinism checks,
and step traces used in the report.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple

EPS = "ε"
Z0 = "Z0"


@dataclass(frozen=True)
class Transition:
    state: str
    input_sym: str  # or EPS
    stack_top: str
    next_state: str
    stack_push: Tuple[str, ...]  # top at the right; empty means pop


class PDA:
    def __init__(
        self,
        name: str,
        states: Iterable[str],
        input_alphabet: Iterable[str],
        stack_alphabet: Iterable[str],
        transitions: Iterable[Transition],
        start: str,
        start_stack: str = Z0,
        accept_states: Optional[Iterable[str]] = None,
        accept_by_empty_stack: bool = False,
        require_bottom_stack: bool = False,
    ):
        self.name = name
        self.states = set(states)
        self.input_alphabet = set(input_alphabet)
        self.stack_alphabet = set(stack_alphabet) | {start_stack}
        self.transitions = list(transitions)
        self.start = start
        self.start_stack = start_stack
        self.accept_states = set(accept_states or [])
        self.accept_by_empty_stack = accept_by_empty_stack
        self.require_bottom_stack = require_bottom_stack
        self._index: Dict[Tuple[str, str, str], List[Transition]] = {}
        for t in self.transitions:
            self._index.setdefault((t.state, t.input_sym, t.stack_top), []).append(t)

    def is_deterministic(self) -> bool:
        """DPDA: unique move per (state, symbol∪{ε}, top), and no ε/input race."""
        keys = set()
        for t in self.transitions:
            key = (t.state, t.input_sym, t.stack_top)
            if key in keys:
                return False
            keys.add(key)
        for state in self.states:
            for top in self.stack_alphabet:
                if (state, EPS, top) not in self._index:
                    continue
                for a in self.input_alphabet:
                    if (state, a, top) in self._index:
                        return False
        return True

    def _applicable(self, state: str, next_input: Optional[str], top: str) -> List[Transition]:
        out: List[Transition] = []
        if next_input is not None:
            out.extend(self._index.get((state, next_input, top), []))
        out.extend(self._index.get((state, EPS, top), []))
        return out

    def run(self, tokens: List[str], max_configs: int = 5000):
        """
        BFS over configurations. Returns (accepted, path, explored).

        ε-moves are always explored for NPDAs. When the machine is
        deterministic, an ε-move on a given stack top is used only if there
        is no input-consuming alternative (or the remaining input is empty).
        That matches the usual DPDA reading convention without an endmarker.
        """
        start_cfg = (self.start, tuple(tokens), (self.start_stack,))
        todo = deque([(start_cfg, [self._fmt(start_cfg)])])
        seen = {start_cfg}
        explored = 0
        deterministic = self.is_deterministic()

        while todo and explored < max_configs:
            (q, w, stack), path = todo.popleft()
            explored += 1
            if self._accepting(q, w, stack):
                return True, path, explored

            top = stack[-1] if stack else None
            if top is None:
                continue
            nxt_sym = w[0] if w else None

            input_moves = []
            if nxt_sym is not None:
                input_moves = list(self._index.get((q, nxt_sym, top), []))
            eps_moves = list(self._index.get((q, EPS, top), []))

            if deterministic:
                if input_moves:
                    candidates = input_moves
                else:
                    candidates = eps_moves
            else:
                candidates = input_moves + eps_moves

            for t in candidates:
                if t.input_sym == EPS:
                    new_w = w
                else:
                    if not w or w[0] != t.input_sym:
                        continue
                    new_w = w[1:]
                new_stack = stack[:-1] + t.stack_push
                # Bound stack growth (blocks left-recursion ε-loops).
                if len(new_stack) > len(tokens) + 8:
                    continue
                cfg = (t.next_state, new_w, new_stack)
                if cfg in seen:
                    continue
                seen.add(cfg)
                todo.append((cfg, path + [self._fmt(cfg)]))

        return False, None, explored

    def accepts(self, tokens: List[str]) -> bool:
        ok, _, _ = self.run(tokens)
        return ok

    def _accepting(self, q, w, stack) -> bool:
        if w:
            return False
        if self.require_bottom_stack and stack != (self.start_stack,):
            return False
        by_state = q in self.accept_states
        by_empty = self.accept_by_empty_stack and len(stack) == 0
        if self.accept_states and self.accept_by_empty_stack:
            return by_state or by_empty
        if self.accept_states:
            return by_state
        return by_empty

    @staticmethod
    def _fmt(cfg) -> str:
        q, w, stack = cfg
        wshow = "".join(w) if w else "ε"
        sshow = "".join(reversed(stack))  # top on the left for readability
        return f"({q}, {wshow}, {sshow})"

    def to_dot(self) -> str:
        lines = [
            f'digraph "{self.name}" {{',
            "  rankdir=LR;",
            '  node [shape=circle];',
            '  start [shape=point];',
            f'  start -> "{self.start}";',
        ]
        for s in sorted(self.states):
            shape = "doublecircle" if s in self.accept_states else "circle"
            lines.append(f'  "{s}" [shape={shape}];')
        buckets: Dict[Tuple[str, str], List[str]] = {}
        for t in self.transitions:
            label = f"{t.input_sym},{t.stack_top}/" + (
                "".join(reversed(t.stack_push)) if t.stack_push else "ε"
            )
            buckets.setdefault((t.state, t.next_state), []).append(label)
        for (p, q), labels in buckets.items():
            joined = "\\n".join(labels)
            lines.append(f'  "{p}" -> "{q}" [label="{joined}"];')
        lines.append("}")
        return "\n".join(lines)


def cfg_to_npda(cfg) -> PDA:
    """Standard one-state NPDA construction (Hopcroft et al.)."""
    q = "q"
    transitions = []
    # expand productions
    for p in cfg.productions:
        transitions.append(
            Transition(q, EPS, p.lhs, q, tuple(reversed(p.rhs)) if p.rhs else tuple())
        )
    # match terminals
    for a in cfg.terminals:
        transitions.append(Transition(q, a, a, q, tuple()))
    # start: ε,Z0 → S Z0 then accept by empty after popping Z0? Use final state via ε on Z0
    transitions.append(Transition(q, EPS, Z0, "qf", tuple()))
    # Actually standard construction: start with S on stack, accept by empty stack.
    # Rebuild cleaner:
    transitions = []
    # Pop Z0, push Z0 then start symbol so the start symbol is on top.
    transitions.append(Transition("qstart", EPS, Z0, q, (Z0, cfg.start)))
    for p in cfg.productions:
        # Reverse so the leftmost RHS symbol sits on top of the stack.
        transitions.append(
            Transition(q, EPS, p.lhs, q, tuple(reversed(p.rhs)) if p.rhs else tuple())
        )
    for a in cfg.terminals:
        transitions.append(Transition(q, a, a, q, tuple()))
    transitions.append(Transition(q, EPS, Z0, "qf", tuple()))
    return PDA(
        name=f"NPDA from {cfg.name}",
        states=["qstart", q, "qf"],
        input_alphabet=cfg.terminals,
        stack_alphabet=cfg.nonterminals | cfg.terminals | {Z0},
        transitions=transitions,
        start="qstart",
        accept_states={"qf"},
    )
