# News Summarizer

A news summarization app built with LangGraph and Claude. Search any topic, get the most relevant articles summarized and scored for quality — live at [news-summarizer-langgraph.streamlit.app](https://news-summarizer-langgraph.streamlit.app)

---

## What it does

Type in a topic. The app fetches recent articles from NewsAPI, ranks them by relevance, summarizes the top ones using Claude, and scores each summary on three dimensions:

- **Faithfulness** — does the summary stay true to the source?
- **Conciseness** — is the summary tight and free of padding?
- **ROUGE-L** — how much of the key content from the original is captured?

If quality scores come back low, the app automatically rewrites the search query and tries again — up to 3 times.

---

## Architecture

Built as a LangGraph state graph with a feedback loop:

```
START → scrape → relevance → summarize → evaluate → router
                                                        |
                                          quality low? → refine → scrape
                                          quality OK?  → END
```

| Node | What it does |
|---|---|
| `scrape` | Fetches articles from NewsAPI and scrapes full text from each URL |
| `relevance` | Scores each article against the topic using Claude as judge, keeps top 3 |
| `summarize` | Summarizes each article in 2–4 sentences using Claude |
| `evaluate` | Scores each summary for faithfulness, conciseness, and ROUGE-L |
| `router` | Exits if quality is sufficient, loops back if not |
| `refine` | Rewrites the search query before the next iteration |

---

## Stack

| Layer | Tool |
|---|---|
| Graph orchestration | LangGraph |
| LLM | Claude Haiku via LangChain Anthropic |
| News source | NewsAPI |
| Scraping | BeautifulSoup |
| Evaluation | LLM-as-Judge + ROUGE-L |
| Frontend | Streamlit |

---

## Run locally

**1. Clone the repo**
```bash
git clone https://github.com/apaarsaroj/news-summarizer.git
cd news-summarizer
```

**2. Add your API keys**
```bash
# .env
ANTHROPIC_API_KEY=your_key
NEWS_API_KEY=your_key
```

**3. Install dependencies**
```bash
uv sync
```

**4. Run**
```bash
streamlit run app.py
```

---

## Project structure

```
news-summarizer/
├── app.py            # Streamlit frontend
├── graph.py          # LangGraph graph definition
├── nodes.py          # Node functions
├── router.py         # Conditional routing logic
├── state.py          # NewsState TypedDict
├── chains.py         # LangChain chains
├── scraper.py        # NewsAPI + BeautifulSoup scraper
├── prompts.py        # Prompt loader
├── config.py         # Configuration constants
└── prompts/          # Prompt files for each chain
```