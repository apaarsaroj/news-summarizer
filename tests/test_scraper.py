import scraper


def article(url, text="x" * 300):
    return {"url": url, "text": text}


def test_deduplicate_keeps_one_article_per_domain():
    items = [
        article("https://a.com/1"),
        article("https://a.com/2"),
        article("https://b.com/1"),
    ]
    result = scraper.deduplicate(items)
    assert [a["url"] for a in result] == ["https://a.com/1", "https://b.com/1"]


def test_fetch_full_text_returns_empty_string_on_error(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr(scraper.requests, "get", boom)
    assert scraper.fetch_full_text("https://a.com") == ""


def test_fetch_full_text_skips_short_paragraphs(monkeypatch):
    html = "<p>short</p><p>" + "long paragraph " * 5 + "</p>"

    class Resp:
        text = html

    monkeypatch.setattr(scraper.requests, "get", lambda *a, **k: Resp())
    text = scraper.fetch_full_text("https://a.com")
    assert "short" not in text
    assert "long paragraph" in text


def test_scrape_falls_back_to_description_when_page_is_empty(monkeypatch):
    raw = [{
        "url": "https://a.com/1",
        "title": "T",
        "source": {"name": "A"},
        "publishedAt": "2026-10-01T00:00:00Z",
        "description": "d" * 150,
        "content": "c" * 150,
    }]
    monkeypatch.setattr(scraper, "get_articles", lambda topic: raw)
    monkeypatch.setattr(scraper, "fetch_full_text", lambda url: "")
    result = scraper.scrape_articles("ai")
    assert len(result) == 1
    assert result[0]["date"] == "2026-10-01"
    assert result[0]["text"].startswith("d")


def test_scrape_does_not_fetch_duplicate_domains(monkeypatch):
    raw = [
        {"url": "https://a.com/1", "title": "T", "source": {}, "publishedAt": "", "description": "d" * 300, "content": ""},
        {"url": "https://a.com/2", "title": "T", "source": {}, "publishedAt": "", "description": "d" * 300, "content": ""},
    ]
    fetched = []
    monkeypatch.setattr(scraper, "get_articles", lambda topic: raw)
    monkeypatch.setattr(scraper, "fetch_full_text", lambda url: fetched.append(url) or "")
    result = scraper.scrape_articles("ai")
    assert fetched == ["https://a.com/1"]
    assert len(result) == 1


def test_scrape_drops_articles_with_no_usable_text(monkeypatch):
    raw = [{"url": "https://a.com/1", "title": "T", "source": {}, "publishedAt": "",
            "description": "", "content": ""}]
    monkeypatch.setattr(scraper, "get_articles", lambda topic: raw)
    monkeypatch.setattr(scraper, "fetch_full_text", lambda url: "")
    assert scraper.scrape_articles("ai") == []
