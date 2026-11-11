#!/usr/bin/env python3
"""Write Graphviz DOT files for PDA diagrams."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pda_cfg.cases import BRACKETS_PDA, PAL_WCWR_PDA, PAL_WWR_PDA  # noqa: E402

OUT = ROOT / "docs" / "diagrams"
OUT.mkdir(parents=True, exist_ok=True)


def write(name: str, dot: str) -> None:
    path = OUT / f"{name}.dot"
    path.write_text(dot)
    print("wrote", path)
    if shutil.which("dot"):
        for fmt in ("png", "svg"):
            dest = OUT / f"{name}.{fmt}"
            subprocess.run(["dot", f"-T{fmt}", "-o", str(dest), str(path)], check=True)
            print("wrote", dest)


def main() -> None:
    write("pda_brackets", BRACKETS_PDA.to_dot())
    write("pda_palindrome_wcwr", PAL_WCWR_PDA.to_dot())
    write("pda_palindrome_wwr", PAL_WWR_PDA.to_dot())


if __name__ == "__main__":
    main()
