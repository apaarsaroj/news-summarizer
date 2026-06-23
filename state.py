from typing import TypedDict, List


class NewsState(TypedDict):
    topic: str                  # User's search query
    articles: List[dict]        # Raw scraped articles from NewsAPI
    scored: List[dict]          # Articles with relevance scores attached
    top_articles: List[dict]    # Top N articles after relevance sorting
    results: List[dict]         # Final articles with summary + eval scores
    iteration: int              # Tracks how many times the graph has looped
    quality_score: float        # Average (faithfulness + conciseness) across results
    status: str                 # Current graph status for debugging