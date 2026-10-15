"""Run the real graph on a fixed set of topics and print average quality numbers.

Needs ANTHROPIC_API_KEY and NEWS_API_KEY in .env. Run from the repo root:
    uv run python scripts/measure.py
"""
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from graph import graph  # noqa: E402

TOPICS = [
    "Artificial Intelligence regulation",
    "Electric vehicle sales",
    "Wind energy",
    "Federal Reserve interest rates",
    "Cybersecurity breach",
    "Climate change policy",
    "Quantum computing",
    "Healthcare AI",
    "Semiconductor supply chain",
    "Space exploration",
]


def run(topic):
    state = {"topic": topic, "articles": [], "scored": [], "top_articles": [],
             "results": [], "iteration": 0, "quality_score": 0.0, "status": "init"}
    start = time.time()
    out = graph.invoke(state)
    return out, time.time() - start


def avg(values):
    return sum(values) / len(values) if values else 0.0


def main():
    rows = []
    for topic in TOPICS:
        try:
            out, secs = run(topic)
        except Exception as exc:
            print(f"FAILED {topic}: {exc}")
            continue
        res = out.get("results", [])
        rows.append({
            "topic": topic,
            "articles": len(res),
            "iterations": out["iteration"],
            "quality": out["quality_score"],
            "faith": avg([r["faithfulness"] for r in res]),
            "concise": avg([r["conciseness"] for r in res]),
            "rouge": avg([r["rouge_l"] for r in res]),
            "secs": secs,
        })
        r = rows[-1]
        print(f"{topic:38} n={r['articles']} iters={r['iterations']} "
              f"quality={r['quality']:.1f} faith={r['faith']:.1f} "
              f"concise={r['concise']:.1f} rougeL={r['rouge']:.1f} {r['secs']:.0f}s")

    if not rows:
        print("No successful runs.")
        return
    refined = sum(1 for r in rows if r["iterations"] > 1)
    print("\n=== SUMMARY ===")
    print(f"topics run:            {len(rows)} of {len(TOPICS)}")
    print(f"avg faithfulness:      {avg([r['faith'] for r in rows]):.1f}")
    print(f"avg conciseness:       {avg([r['concise'] for r in rows]):.1f}")
    print(f"avg ROUGE-L:           {avg([r['rouge'] for r in rows]):.1f}")
    print(f"avg quality score:     {avg([r['quality'] for r in rows]):.1f}")
    print(f"needed refine loop:    {refined} of {len(rows)}")
    print(f"avg seconds per run:   {avg([r['secs'] for r in rows]):.0f}")


if __name__ == "__main__":
    main()
