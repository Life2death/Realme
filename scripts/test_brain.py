#!/usr/bin/env python3
"""
Phase 1 brain-validation harness for the Realme AI advisor.

This is the Gate 1 tool (see docs/PIPELINE.md). It loads the system prompt
(prompts/system-prompt.md) plus the entire knowledge base (data/qa/*.md)
into a single prompt-cached context — via scripts/brain.py, the single
source of truth for the brain also used by server/llm_proxy.py in Phase 2 —
then lets you either:

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
    # or just create a .env file at the repo root — it's loaded automatically.
    python scripts/test_brain.py            # interactive chat
    python scripts/test_brain.py --eval     # batch eval with scoring prompts
"""

from __future__ import annotations

import argparse

import anthropic

import brain

# The brain will eventually drive a real-time voice agent, where latency and
# per-minute cost matter. claude-opus-4-8 is the highest-quality option and a
# good baseline for judging whether the KNOWLEDGE BASE itself is good enough.
# For the production voice pipeline (server/llm_proxy.py), claude-sonnet-5 is
# materially cheaper and faster, and often indistinguishable for this kind of
# Q&A. Swap here and re-run the eval to compare.
MODEL = "claude-opus-4-8"

# BLUF answers are short; 2048 is plenty and keeps latency realistic for the
# voice use case. Raise only if you see answers truncated mid-sentence.
MAX_TOKENS = 2048


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
        if brain.ESCALATION_MARKER in answer.lower():
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
        escalated = brain.ESCALATION_MARKER in answer.lower()
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

    anthropic_key = brain.require_env(
        "ANTHROPIC_API_KEY",
        "Either export it in your shell, or create a .env file at the repo "
        "root (see scripts/.env.example).",
    )
    client = anthropic.Anthropic(api_key=anthropic_key)
    system_blocks = brain.load_system_blocks()

    if args.eval:
        run_eval(client, system_blocks)
    else:
        run_interactive(client, system_blocks)


if __name__ == "__main__":
    main()
