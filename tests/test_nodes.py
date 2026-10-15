import nodes
from config import TOP_N


class FakeChain:
    def __init__(self, reply):
        self.reply = reply

    def invoke(self, _inputs):
        return self.reply(_inputs) if callable(self.reply) else self.reply


def base_state(**kw):
    s = {"topic": "ai", "articles": [], "scored": [], "top_articles": [],
         "results": [], "iteration": 0, "quality_score": 0.0, "status": "init"}
    s.update(kw)
    return s


def test_scrape_node_increments_iteration(monkeypatch):
    monkeypatch.setattr(nodes, "scrape_articles", lambda topic: [{"title": "t"}])
    out = nodes.scrape_node(base_state(iteration=1))
    assert out["iteration"] == 2
    assert out["articles"] == [{"title": "t"}]


def test_relevance_node_keeps_top_n_sorted(monkeypatch):
    arts = [{"title": str(i), "text": str(i)} for i in range(6)]
    monkeypatch.setattr(nodes, "relevance_chain", FakeChain(lambda i: i["article"]))
    out = nodes.relevance_node(base_state(articles=arts))
    assert len(out["top_articles"]) == TOP_N
    scores = [a["relevance"] for a in out["top_articles"]]
    assert scores == sorted(scores, reverse=True)
    assert scores[0] == 5


def test_relevance_node_treats_non_numeric_reply_as_zero(monkeypatch):
    monkeypatch.setattr(nodes, "relevance_chain", FakeChain("not a number"))
    out = nodes.relevance_node(base_state(articles=[{"title": "t", "text": "x"}]))
    assert out["scored"][0]["relevance"] == 0


def test_summarize_node_attaches_summary(monkeypatch):
    monkeypatch.setattr(nodes, "summarization_chain", FakeChain("short summary"))
    out = nodes.summarize_node(base_state(top_articles=[{"title": "t", "text": "body"}]))
    assert out["results"][0]["summary"] == "short summary"


def test_evaluate_node_averages_scores(monkeypatch):
    monkeypatch.setattr(nodes, "faithfulness_chain", FakeChain("80"))
    monkeypatch.setattr(nodes, "conciseness_chain", FakeChain("60"))
    results = [{"title": "t", "text": "the cat sat on the mat", "summary": "the cat sat"}]
    out = nodes.evaluate_node(base_state(results=results))
    r = out["results"][0]
    assert (r["faithfulness"], r["conciseness"]) == (80, 60)
    assert out["quality_score"] == 70
    assert 0 <= r["rouge_l"] <= 100


def test_parse_score_extracts_and_clamps():
    assert nodes.parse_score("85") == 85
    assert nodes.parse_score("Score: 72.") == 72
    assert nodes.parse_score("250") == 100
    assert nodes.parse_score("no number") == 0


def test_evaluate_node_handles_bad_judge_output(monkeypatch):
    monkeypatch.setattr(nodes, "faithfulness_chain", FakeChain("high"))
    monkeypatch.setattr(nodes, "conciseness_chain", FakeChain("90"))
    results = [{"title": "t", "text": "abc", "summary": "abc"}]
    out = nodes.evaluate_node(base_state(results=results))
    assert out["results"][0]["faithfulness"] == 0
    assert out["quality_score"] == 45


def test_evaluate_node_with_no_results_scores_zero():
    out = nodes.evaluate_node(base_state(results=[]))
    assert out["quality_score"] == 0.0


def test_refine_node_replaces_topic(monkeypatch):
    class Resp:
        content = "  better query  "

    class FakeLLM:
        def invoke(self, prompt):
            return Resp()

    monkeypatch.setattr(nodes, "llm", FakeLLM())
    out = nodes.refine_query_node(base_state(topic="ai", iteration=1))
    assert out["topic"] == "better query"
