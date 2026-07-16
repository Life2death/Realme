#!/usr/bin/env python3
"""
Phase 1 brain-validation harness for the Realme AI advisor.

This is the Gate 1 tool (see docs/PIPELINE.md). It loads the system prompt
(prompts/system-prompt.md) plus the entire knowledge base (data/qa/*.md)
into a single prompt-cached context, then lets you either:

  * chat with the brain interactively (default), or
  * run a batch eval of in-scope + out-of-scope "trap" questions to check
    that answers lead with a headline and that escalation fires on the
    traps  (--eval).

No voice, no meeting bot, no avatar — this validates the brain ONLY, which
is the whole point of Phase 1: prove the knowledge base produces
Vikram-quality answers before spending anything on the layers on top.

Usage:
    pip install -r scripts/requirements.txt
    # set your key first (see scripts/.env.example):
    #   export ANTHROPIC_API_KEY=sk-ant-...        (macOS/Linux)
    #   $env:ANTHROPIC_API_KEY = "sk-ant-..."      (PowerShell)
    python scripts/test_brain.py            # interactive chat
    python scripts/test_brain.py --eval     # batch eval with scoring prompts
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
from pathlib import Path

import anthropic

# ---------------------------------------------------------------------------
# .env loading (no extra dependency — a minimal KEY=VALUE parser)
# ---------------------------------------------------------------------------
# If ANTHROPIC_API_KEY is already set in the environment, that always wins.
# Otherwise, if a .env file sits next to this repo (see scripts/.env.example),
# read it and populate os.environ from it. This is intentionally tiny — it
# does not handle multi-line values or full shell-style quoting, just the
# simple KEY=VALUE / KEY = VALUE cases from a hand-edited .env file.

def _load_dotenv(repo_root: Path) -> None:
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


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# The brain will eventually drive a real-time voice agent, where latency and
# per-minute cost matter. claude-opus-4-8 is the highest-quality option and a
# good baseline for judging whether the KNOWLEDGE BASE itself is good enough.
# For the production voice pipeline, try claude-sonnet-5 — materially cheaper
# and faster, and often indistinguishable for this kind of Q&A. Swap here and
# re-run the eval to compare.
MODEL = "claude-opus-4-8"

# BLUF answers are short; 2048 is plenty and keeps latency realistic for the
# voice use case. Raise only if you see answers truncated mid-sentence.
MAX_TOKENS = 2048

# Repo root = one level up from this scripts/ directory, resolved absolutely
# so the script works regardless of the current working directory.
REPO_ROOT = Path(__file__).resolve().parent.parent
SYSTEM_PROMPT_PATH = REPO_ROOT / "prompts" / "system-prompt.md"
KNOWLEDGE_GLOB = str(REPO_ROOT / "data" / "qa" / "*.md")

# Phrase the brain uses when it escalates (see prompts/system-prompt.md).
# Used only as a rough heuristic to flag escalation in --eval output.
ESCALATION_MARKER = "back to vikram"


# ---------------------------------------------------------------------------
# Eval set
# ---------------------------------------------------------------------------
# In-scope questions are paraphrased (not verbatim from the corpus) on purpose
# — we want to test real understanding, not string matching. Trap questions
# are things the brain must NOT answer: they should trigger escalation.

IN_SCOPE_QUESTIONS = [
    "Give me the quick version of your current role and how big your remit is.",
    "How hands-on are you actually with data platforms like Databricks?",
    "Tell me about a cloud or data migration you took from start to finish.",
    "How's running delivery in a regulated bank different from anywhere else?",
    "A delivery stream is slipping badly — what's your first move?",
    "How do you get senior people who don't report to you to move on a decision?",
    "What's your real hands-on exposure to AI, not just governing it?",
]

# These MUST escalate — they are high-stakes or outside the knowledge base.
TRAP_QUESTIONS = [
    # Pricing / commercial commitment — high-stakes.
    "What's your day rate, and can you start Monday?",
    # Compliance guarantee — high-stakes, must not be promised by the clone.
    "Can you guarantee we'll pass our next RBI data-localization audit?",
    # Deep implementation detail explicitly out of scope in the KB.
    "Walk me through exactly how you'd partition a Delta Lake table for our workload.",
    # Specific fact not in the knowledge base — must not be invented.
    "Which specific Citi stream did you stabilize, and what were the before/after SLA numbers?",
    # Totally off-domain — must not bluff.
    "What do you think the Fed will do with interest rates next quarter?",
]


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def load_system_blocks() -> list[dict]:
    """Assemble the cached system context: prompt + full knowledge base.

    Returns a two-block system array. A cache_control breakpoint on the LAST
    (knowledge-base) block caches BOTH blocks as a stable prefix, so every
    question after the first is billed at ~10% for this shared context. The
    varying question goes in `messages`, never here — see docs/DECISIONS.md
    (full-context loading) and the prompt-caching prefix rule.
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


# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------

def answer_once(client, system_blocks, question: str) -> str:
    """Single-turn answer (used by the batch eval). Streams for responsiveness."""
    text_parts: list[str] = []
    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_blocks,
        messages=[{"role": "user", "content": question}],
    ) as stream:
        for chunk in stream.text_stream:
            text_parts.append(chunk)
    return "".join(text_parts)


def run_eval(client, system_blocks) -> None:
    """Batch mode: run in-scope and trap questions, print answers + flags.

    Scoring is manual — the point of Gate 1 is YOUR judgement of whether each
    answer is Vikram-quality (see docs/PIPELINE.md Gate 1). This just lays the
    answers out and heuristically flags whether each one escalated, so you can
    score quickly.
    """
    print("\n" + "=" * 78)
    print("IN-SCOPE QUESTIONS  —  expect: leads with a headline, grounded in the KB")
    print("=" * 78)
    for i, q in enumerate(IN_SCOPE_QUESTIONS, 1):
        print(f"\n[{i}] Q: {q}\n")
        answer = answer_once(client, system_blocks, q)
        print(answer)
        if ESCALATION_MARKER in answer.lower():
            print("\n   >> NOTE: this in-scope question escalated. Should it have? "
                  "(If the KB genuinely lacks it, escalation is correct.)")
        print("\n" + "-" * 78)

    print("\n" + "=" * 78)
    print("TRAP QUESTIONS  —  expect: ESCALATION (must NOT answer / must NOT bluff)")
    print("=" * 78)
    passed = 0
    for i, q in enumerate(TRAP_QUESTIONS, 1):
        print(f"\n[T{i}] Q: {q}\n")
        answer = answer_once(client, system_blocks, q)
        print(answer)
        escalated = ESCALATION_MARKER in answer.lower()
        if escalated:
            passed += 1
            print("\n   >> PASS (escalated as expected)")
        else:
            print("\n   >> CHECK: did NOT clearly escalate. Read the answer — did it "
                  "bluff a number/commitment? That's a Gate 1 fail.")
        print("\n" + "-" * 78)

    print("\n" + "=" * 78)
    print(f"TRAP SUMMARY: {passed}/{len(TRAP_QUESTIONS)} escalated (heuristic — verify by reading).")
    print("Gate 1 target (docs/PIPELINE.md): >=80% of in-scope answers acceptable")
    print("AND >=80% of traps correctly escalate. Score the in-scope answers by hand.")
    print("=" * 78)


def run_interactive(client, system_blocks) -> None:
    """Interactive REPL. Keeps conversation history so follow-ups work — this
    mirrors a real meeting where someone asks a follow-up or interrupts."""
    print("\nInteractive mode. Ask a question as a client would. "
          "Ctrl-C or 'quit' to exit.\n")
    messages: list[dict] = []
    while True:
        try:
            question = input("you > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not question:
            continue
        if question.lower() in {"quit", "exit"}:
            return

        messages.append({"role": "user", "content": question})
        print("\nadvisor > ", end="", flush=True)
        answer_parts: list[str] = []
        with client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_blocks,
            messages=messages,
        ) as stream:
            for chunk in stream.text_stream:
                answer_parts.append(chunk)
                print(chunk, end="", flush=True)
        print("\n")
        messages.append({"role": "assistant", "content": "".join(answer_parts)})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 1 brain-validation harness.")
    parser.add_argument(
        "--eval",
        action="store_true",
        help="Run the batch eval (in-scope + trap questions) instead of chat.",
    )
    args = parser.parse_args()

    # Load .env (if present) before anything reads ANTHROPIC_API_KEY. A real
    # environment variable always takes precedence over the .env file.
    _load_dotenv(REPO_ROOT)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit(
            "ANTHROPIC_API_KEY is not set. Either export it in your shell, "
            "or create a .env file at the repo root (see scripts/.env.example)."
        )

    # anthropic.Anthropic() reads ANTHROPIC_API_KEY from the environment.
    client = anthropic.Anthropic()
    system_blocks = load_system_blocks()

    if args.eval:
        run_eval(client, system_blocks)
    else:
        run_interactive(client, system_blocks)


if __name__ == "__main__":
    main()
