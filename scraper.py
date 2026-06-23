import os
from newsapi import NewsApiClient
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from config import NUM_ARTICLES, MIN_CHARS

def get_articles(topic):
    newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))
    response = newsapi.get_everything(
        q=topic,
        language="en",
        sort_by="relevancy",
        page_size=NUM_ARTICLES * 2
    )
    return response["articles"]

def fetch_full_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        cleaned = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 40]
        text = " ".join(cleaned)
        return text.strip()
    except Exception:
        return ""

def deduplicate(articles):
    seen_domains = set()
    unique = []
    for article in articles:
        domain = urlparse(article["url"]).netloc
        if domain not in seen_domains:
            seen_domains.add(domain)
            unique.append(article)
    return unique

def scrape_articles(topic):
    raw_articles = get_articles(topic)
    articles = []

    for article in raw_articles:
        url = article["url"]
        text = fetch_full_text(url)

        title = article.get("title") or "Untitled"
        source = article.get("source", {}).get("name") or "Unknown Source"
        date = article.get("publishedAt", "")[:10]

        if len(text) > MIN_CHARS:
            articles.append({
                "url": url,
                "text": text,
                "title": title,
                "source": source,
                "date": date,
            })
        else:
            description = article.get("description") or ""
            content = article.get("content") or ""
            fallback = description + " " + content
            if len(fallback) > MIN_CHARS:
                articles.append({
                    "url": url,
                    "text": fallback,
                    "title": title,
                    "source": source,
                    "date": date,
                })

    articles = deduplicate(articles)
    return articles