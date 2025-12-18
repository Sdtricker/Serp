# main.py
import requests
from bs4 import BeautifulSoup
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",  # no br
    "Referer": "https://search.brave.com/",
}

URL = "https://search.brave.com/search"

def fetch_page(query, offset, seen):
    params = {
        "q": query,
        "source": "web",
        "offset": offset
    }

    try:
        r = requests.get(URL, headers=HEADERS, params=params, timeout=20)
        r.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    results = []

    for a in soup.find_all("a", href=True):
        link = a["href"].strip()
        title = a.get_text(strip=True)

        if not link.startswith("http"):
            continue
        if "brave.com" in link:
            continue
        if not title or title == link:
            continue
        if link in seen:
            continue

        seen.add(link)
        results.append((title, link))

    return results


def handler(request):
    query = request.args.get("query", "").strip()

    if not query:
        return """
        <h2>❌ Error: Missing ?query= parameter</h2>
        <p>Example: <code>?query=how+to+bake+a+cake</code></p>
        <hr>
        <a href="https://t.me/NGYT777GGG" target="_blank">
            <h3>💬 Made by @NGYT777GGG (Click to Join Telegram)</h3>
        </a>
        """, 400, {"Content-Type": "text/html; charset=utf-8"}

    seen = set()
    all_results = []
    max_pages = 3  # Always first 3 pages
    offset = 0

    for page in range(1, max_pages + 1):
        page_results = fetch_page(query, offset, seen)
        if not page_results:
            break
        all_results.extend(page_results)
        offset += 10

    # Build HTML Response
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🦁 Brave Search Results for "{query}"</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 30px; background: #f9f9f9; }}
            .result {{ margin-bottom: 25px; }}
            .title {{ font-size: 18px; color: #1a0dab; text-decoration: none; font-weight: bold; }}
            .link {{ color: #006621; word-break: break-all; }}
            hr {{ margin: 30px 0; }}
            footer {{ margin-top: 40px; padding: 20px; background: #eee; border-radius: 8px; text-align: center; }}
            footer a {{ color: #ff5722; font-weight: bold; font-size: 18px; }}
        </style>
    </head>
    <body>
        <h1>🦁 Brave Search Results</h1>
        <p><strong>Query:</strong> {query}</p>
        <p><strong>Total Results:</strong> {len(all_results)}</p>
        <hr>
    """

    for i, (title, link) in enumerate(all_results, 1):
        html += f"""
        <div class="result">
            <div><strong>{i}.</strong> <a href="{link}" class="title" target="_blank">{title}</a></div>
            <div class="link">🔗 {link}</div>
        </div>
        """

    # FOOTER WITH CLICKABLE MADE BY
    html += f"""
        <hr>
        <footer>
            <a href="https://t.me/NGYT777GGG" target="_blank">
                💬 Made by @NGYT777GGG (Click to Join on Telegram)
            </a>
        </footer>
    </body>
    </html>
    """

    return html, 200, {"Content-Type": "text/html; charset=utf-8"}


# Vercel entry point
def handler_wrapper(request):
    from flask import Flask, request as flask_request

    app = Flask(__name__)

    @app.route('/', methods=['GET'])
    def serve():
        return handler(flask_request)

    return app


# This is required for Vercel serverless function
app = handler_wrapper(None)