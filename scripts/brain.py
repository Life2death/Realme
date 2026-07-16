"""
Shared "brain" logic for the Realme AI advisor: loads the system prompt +
knowledge base into a prompt-cached context, and loads .env.

This module is the single source of truth for what the brain knows and how
it's configured. Both scripts/test_brain.py (Phase 1 text eval) and
server/llm_proxy.py (Phase 2 voice proxy) import from here — this guarantees
Phase 2 talks to the EXACT brain that passed Gate 1, not a hand-copied
duplicate. See docs/DECISIONS.md for why this matters.

Do not duplicate load_system_blocks() elsewhere. If the brain needs to
change (new system prompt, new knowledge files), change it here once.
"""

from __future__ import annotations

import glob
import os
import sys
from pathlib import Path

# Repo root = one level up from this scripts/ directory, resolved absolutely
# so this module works regardless of the current working directory or which
# script imports it.
REPO_ROOT = Path(__file__).resolve().parent.parent
SYSTEM_PROMPT_PATH = REPO_ROOT / "prompts" / "system-prompt.md"
KNOWLEDGE_GLOB = str(REPO_ROOT / "data" / "qa" / "*.md")

# Phrase the brain uses when it escalates (see prompts/system-prompt.md).
# Used only as a rough heuristic by callers that want to flag escalation.
ESCALATION_MARKER = "back to vikram"


# ---------------------------------------------------------------------------
# .env loading (no extra dependency — a minimal KEY=VALUE parser)
# ---------------------------------------------------------------------------
# If a variable is already set in the real environment, that always wins.
# Otherwise, if a .env file sits at the repo root (see scripts/.env.example),
# read it and populate os.environ from it. Intentionally tiny — no
# multi-line values, no full shell-style quoting, just simple
# KEY=VALUE / KEY = VALUE lines from a hand-edited .env file.

def load_dotenv(repo_root: Path = REPO_ROOT) -> None:
    env_path = repo_root / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def require_env(name: str, hint: str) -> str:
    """Load .env then fetch a required env var, or exit with a clear message."""
    load_dotenv()
    value = os.environ.get(name)
    if not value:
        sys.exit(f"{name} is not set. {hint}")
    return value


# ---------------------------------------------------------------------------
# The brain itself
# ---------------------------------------------------------------------------

def load_system_blocks() -> list[dict]:
    """Assemble the cached system context: prompt + full knowledge base.

    Returns a two-block system array. A cache_control breakpoint on the LAST
    (knowledge-base) block caches BOTH blocks as a stable prefix, so every
    question after the first is billed at ~10% for this shared context. The
    varying question/conversation goes in `messages`, never here — see
    docs/DECISIONS.md (full-context loading) and the prompt-caching prefix
    rule.
    """
    if not SYSTEM_PROMPT_PATH.exists():
        sys.exit(f"System prompt not found: {SYSTEM_PROMPT_PATH}")

    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

    kb_files = sorted(glob.glob(KNOWLEDGE_GLOB))
    if not kb_files:
        sys.exit(f"No knowledge-base files found matching: {KNOWLEDGE_GLOB}")

    kb_parts = []
    for path in kb_files:
        kb_parts.append(f"===== FILE: {Path(path).name} =====\n")
        kb_parts.append(Path(path).read_text(encoding="utf-8"))
        kb_parts.append("\n\n")
    knowledge_base = "".join(kb_parts)

    print(f"Loaded system prompt + {len(kb_files)} knowledge file(s):", file=sys.stderr)
    for path in kb_files:
        print(f"  - {Path(path).name}", file=sys.stderr)

    return [
        {"type": "text", "text": system_prompt},
        {
            "type": "text",
            "text": "KNOWLEDGE BASE\n\n" + knowledge_base,
            # Cache the stable prefix (prompt + KB). Prefix-match caching means
            # this one breakpoint covers both blocks.
            "cache_control": {"type": "ephemeral"},
        },
    ]
