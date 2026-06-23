from langgraph.graph import StateGraph, START, END
from state import NewsState
from nodes import scrape_node, relevance_node, summarize_node, evaluate_node, refine_query_node
from router import should_continue


def build_graph():
    workflow = StateGraph(NewsState)

    # Register nodes
    workflow.add_node("scrape", scrape_node)
    workflow.add_node("relevance", relevance_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("evaluate", evaluate_node)
    workflow.add_node("refine", refine_query_node)

    # Linear flow
    workflow.add_edge(START, "scrape")
    workflow.add_edge("scrape", "relevance")
    workflow.add_edge("relevance", "summarize")
    workflow.add_edge("summarize", "evaluate")

    # Conditional exit or loop via refine
    workflow.add_conditional_edges(
        "evaluate",
        should_continue,
        {
            "scrape": "refine",
            "end": END
        }
    )

    workflow.add_edge("refine", "scrape")

    return workflow.compile()


graph = build_graph()