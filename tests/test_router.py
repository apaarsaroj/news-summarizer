from config import MAX_ITERATIONS, QUALITY_THRESHOLD
from router import should_continue


def state(iteration, quality):
    return {"iteration": iteration, "quality_score": quality}


def test_exits_when_quality_meets_threshold():
    assert should_continue(state(1, QUALITY_THRESHOLD)) == "end"


def test_loops_when_quality_is_low():
    assert should_continue(state(1, QUALITY_THRESHOLD - 1)) == "scrape"


def test_exits_at_max_iterations_even_if_quality_is_low():
    assert should_continue(state(MAX_ITERATIONS, 0.0)) == "end"
