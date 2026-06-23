from chains import summarization_chain, similaritychecker_chain, hallucinationchecker_chain, relevance_chain, llm
from scraper import scrape_articles
from state import NewsState
from config import MAX_CHARS, TOP_N
from rouge_score import rouge_scorer

def scrape_node(state: NewsState) -> dict:
    print(f"\n[scrape] iteration {state['iteration'] + 1}")
    articles = scrape_articles(state["topic"])
    print(f"[scrape] fetched {len(articles)} articles")
    return {
        "articles": articles,
        "iteration": state["iteration"] + 1,
        "status": "scraped"
    }


def relevance_node(state: NewsState) -> dict:
    print(f"\n[relevance] scoring {len(state['articles'])} articles")
    scored = []
    for article in state["articles"]:
        score = relevance_chain.invoke({
            "topic": state["topic"],
            "article": article["text"][:MAX_CHARS]
        })
        try:
            relevance = int(score)
        except ValueError:
            relevance = 0
        scored.append({**article, "relevance": relevance})

    top_articles = sorted(scored, key=lambda x: x["relevance"], reverse=True)[:TOP_N]
    print(f"[relevance] kept top {len(top_articles)}")
    return {
        "scored": scored,
        "top_articles": top_articles,
        "status": "scored"
    }


def summarize_node(state: NewsState) -> dict:
    print(f"\n[summarize] summarizing {len(state['top_articles'])} articles")
    results = []
    for article in state["top_articles"]:
        text_slice = article["text"][:MAX_CHARS]
        summary = summarization_chain.invoke({"text": text_slice})
        results.append({**article, "summary": summary})
        print(f"[summarize] done: {article['title'][:60]}")
    return {
        "results": results,
        "status": "summarized"
    }



def evaluate_node(state: NewsState) -> dict:
    print(f"\n[evaluate] running LLM-as-Judge on {len(state['results'])} articles")
    evaluated = []
    total_score = 0.0
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)

    for article in state["results"]:
        text_slice = article["text"][:MAX_CHARS]
        faithfulness = similaritychecker_chain.invoke({
            "text": text_slice,
            "summary": article["summary"]
        })
        conciseness = hallucinationchecker_chain.invoke({
            "text": text_slice,
            "summary": article["summary"]
        })

        try:
            f_score = int(faithfulness)
        except ValueError:
            f_score = 0
        try:
            c_score = int(conciseness)
        except ValueError:
            c_score = 0

        rouge = scorer.score(text_slice, article["summary"])
        rouge_l = round(rouge["rougeL"].fmeasure * 100, 1)

        avg = (f_score + c_score) / 2
        total_score += avg

        evaluated.append({
            **article,
            "faithfulness": f_score,
            "conciseness": c_score,
            "rouge_l": rouge_l
        })
        print(f"[evaluate] faithfulness: {f_score}  conciseness: {c_score}  rouge-L: {rouge_l}")

    quality_score = total_score / len(evaluated) if evaluated else 0.0
    print(f"[evaluate] overall quality score: {quality_score:.1f}")

    return {
        "results": evaluated,
        "quality_score": quality_score,
        "status": "evaluated"
    }

def refine_query_node(state: NewsState) -> dict:
    print(f"\n[refine] rewriting query for iteration {state['iteration']}")
    prompt = f"""The search query '{state['topic']}' returned articles with low quality scores.
Rewrite it as a more specific and targeted news search query.
Return only the new query, nothing else."""

    response = llm.invoke(prompt)
    refined = response.content.strip()
    print(f"[refine] new query: {refined}")
    return {
        "topic": refined,
        "status": "query_refined"
    }