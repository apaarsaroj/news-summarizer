import graph as graph_module
import nodes


def initial():
    return {"topic": "ai", "articles": [], "scored": [], "top_articles": [],
            "results": [], "iteration": 0, "quality_score": 0.0, "status": "init"}


def stub_pipeline(monkeypatch, qualities):
    """Patch the node functions the compiled graph calls, via fresh build."""
    calls = {"scrape": 0}
    quality_iter = iter(qualities)

    def scrape(state):
        calls["scrape"] += 1
        return {"articles": [{"title": "t", "text": "x"}],
                "iteration": state["iteration"] + 1, "status": "scraped"}

    def relevance(state):
        return {"scored": [], "top_articles": state["articles"], "status": "scored"}

    def summarize(state):
        return {"results": [{"title": "t", "summary": "s"}], "status": "summarized"}

    def evaluate(state):
        return {"quality_score": next(quality_iter), "status": "evaluated"}

    def refine(state):
        return {"topic": state["topic"] + " refined", "status": "query_refined"}

    monkeypatch.setattr(graph_module, "scrape_node", scrape)
    monkeypatch.setattr(graph_module, "relevance_node", relevance)
    monkeypatch.setattr(graph_module, "summarize_node", summarize)
    monkeypatch.setattr(graph_module, "evaluate_node", evaluate)
    monkeypatch.setattr(graph_module, "refine_query_node", refine)
    return calls


def test_graph_stops_after_one_pass_when_quality_is_good(monkeypatch):
    calls = stub_pipeline(monkeypatch, [90])
    out = graph_module.build_graph().invoke(initial())
    assert calls["scrape"] == 1
    assert out["topic"] == "ai"


def test_graph_refines_and_retries_when_quality_is_low(monkeypatch):
    calls = stub_pipeline(monkeypatch, [10, 90])
    out = graph_module.build_graph().invoke(initial())
    assert calls["scrape"] == 2
    assert out["topic"] == "ai refined"


def test_graph_gives_up_after_max_iterations(monkeypatch):
    calls = stub_pipeline(monkeypatch, [0, 0, 0, 0, 0])
    graph_module.build_graph().invoke(initial())
    assert calls["scrape"] == 3
