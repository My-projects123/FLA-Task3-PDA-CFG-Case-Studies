# Case Studies with Pushdown Automata and Context-Free Grammars

**Course:** 21CSC301T Formal Language and Automata, CLA-2, Assessment Task 3  
**Student:** Deepak V. F. (RA2411026050015), B.Tech AIML 'A', III year  
**Faculty:** Dr. C. Gunasundari, SRM IST Tiruchirappalli

| # | Case study | Grammar | PDA | Deterministic? |
|---|---|---|---|---|
| 1 | Balanced brackets / code syntax checker | ambiguous `S → SS \| …`, fixed to `S → BS \| B` | DPDA | yes |
| 2 | Arithmetic expression validation | ambiguous `E → E+E \| E*E`, fixed by precedence + LL(1) | CFG→NPDA + LL(1) parser | NPDA no; LL(1) yes |
| 3 | Palindrome checker | `S → aSa \| bSb \| a \| b \| ε` | DPDA for `w c wR`, NPDA for `w wR` | yes / no |

## Live demo

```bash
open docs/index.html
# or: python3 -m http.server 8766 --directory docs
```

Pick brackets, expressions, or palindromes. The control state and stack update as you type; expressions show the LL(1) parse-stack trace.

## Run the CLI and tests

```bash
pip install -r requirements.txt
python3 -m pda_cfg.cli all
python3 -m pda_cfg.cli brackets
python3 -m pda_cfg.cli expr
python3 -m pda_cfg.cli palindrome
python3 -m pda_cfg.cli ambiguity
python3 -m pytest -q
python3 tools/make_diagrams.py   # optional; needs Graphviz `dot`
```

## Why a DFA is not enough

L = { (ⁿ )ⁿ } is not regular (pumping lemma). The same idea blocks palindromes and nested expressions. A PDA’s stack is exactly the LIFO memory nesting needs.

## Layout

```
pda_cfg/         CFG, PDA, LL(1), case studies, CLI
tests/           sample + exhaustive checks
docs/index.html  live browser demo
docs/diagrams/   Graphviz DOT sources
tools/
```
