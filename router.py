from typing import Literal
from state import NewsState
from config import MAX_ITERATIONS, QUALITY_THRESHOLD


def should_continue(state: NewsState) -> Literal["scrape", "end"]:
    print(f"\n[router] iteration: {state['iteration']}  quality: {state['quality_score']:.1f}  threshold: {QUALITY_THRESHOLD}")

    if state["iteration"] >= MAX_ITERATIONS:
        print(f"[router] max iterations reached, exiting")
        return "end"

    if state["quality_score"] >= QUALITY_THRESHOLD:
        print(f"[router] quality sufficient, exiting")
        return "end"

    print(f"[router] quality below threshold, looping back to scrape")
    return "scrape"