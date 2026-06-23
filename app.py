import os
import streamlit as st
from dotenv import load_dotenv
from graph import graph

load_dotenv()

if "ANTHROPIC_API_KEY" in st.secrets:
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
if "NEWS_API_KEY" in st.secrets:
    os.environ["NEWS_API_KEY"] = st.secrets["NEWS_API_KEY"]

st.set_page_config(page_title="News Summarizer", layout="centered")

st.title("News Summarizer")
st.caption("Search any topic. We find the most relevant articles, summarize them, and score them for you.")

topic = st.text_input("Enter a topic", placeholder="e.g. Artificial Intelligence")

if st.button("Search") and topic.strip():
    with st.spinner("Fetching and summarizing articles..."):
        initial_state = {
            "topic": topic,
            "articles": [],
            "scored": [],
            "top_articles": [],
            "results": [],
            "iteration": 0,
            "quality_score": 0.0,
            "status": "initialized"
        }
        result = graph.invoke(initial_state)

    if not result["results"]:
        st.error("No articles found. Try a different topic.")
    else:
        st.success(f"Top {len(result['results'])} articles for: **{topic}**")
        st.divider()

        for i, article in enumerate(result["results"], 1):
            st.subheader(f"{i}. {article['title']}")
            st.caption(f"{article['source']}  ·  {article['date']}  ·  Relevance: {article['relevance']}%")
            st.write(article["summary"])

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Faithfulness", f"{article['faithfulness']}%")
                st.progress(article["faithfulness"] / 100)
            with col2:
                st.metric("Conciseness", f"{article['conciseness']}%")
                st.progress(article["conciseness"] / 100)
            with col3:
                st.metric("ROUGE-L", f"{article['rouge_l']}%")
                st.progress(article["rouge_l"] / 100)

            st.markdown(f"[Read full article]({article['url']})")
            st.divider()