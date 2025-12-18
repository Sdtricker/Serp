
# main.py
from flask import Flask, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
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
    except Exception as e:
        print(f"[ERROR] Fetch failed: {e}")
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


@app.route('/', methods=['GET'])
def search():
    query = request.args.get("query", "").strip()

    if not query:
        return """
        <h2>❌ Error: Missing ?query= parameter</h2>
        <p>Example: <code>?query=how+to+bake+a+cake</code></p>
        <hr>
        <center>
        <a href="https://t.me/NGYT777GGG" target="_blank" style="font-size:20px; color:#ff5722; text-decoration:none;">
            💬 Made by @NGYT777GGG (Click to Join Telegram)
        </a>
        </center>
        """, 400

    seen = set()
    all_results = []
    max_pages = 3
    offset = 0

    for page in range(1, max_pages + 1):
        page_results = fetch_page(query, offset, seen)
        if not page_results:
            break
        all_results.extend(page_results)
        offset += 10

    # Start building HTML response
    html_parts = [
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>🦁 Brave Search Results</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .result { margin: 20px 0; padding: 15px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .title { font-size: 18px; color: #1a0dab; text-decoration: none; font-weight: bold; display: block; margin-bottom: 5px; }
                .link { color: #006621; word-break: break-all; font-size: 14px; }
                hr { margin: 30px 0; border: none; border-top: 1px solid #ddd; }
                footer { margin-top: 40px; padding: 20px; background: #eee; border-radius: 8px; text-align: center; }
                footer a { color: #ff5722; font-weight: bold; font-size: 18px; text-decoration: none; }
                footer a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>🦁 Brave Search Results for "<i>{}</i>"</h1>
            <p><strong>✅ Showing first 3 pages | Total Results: {}</strong></p>
            <hr>
        """.format(query, len(all_results))
    ]

    for i, (title, link) in enumerate(all_results, 1):
        html_parts.append(f"""
        <div class="result">
            <a href="{link}" class="title" target="_blank">{i}. {title}</a>
            <div class="link">🔗 {link}</div>
        </div>
        """)

    html_parts.append("""
        <hr>
        <footer>
            <a href="https://t.me/NGYT777GGG" target="_blank">
                💬 Made by @NGYT777GGG (Click to Join on Telegram)
            </a>
        </footer>
        </body>
        </html>
    """)

    full_html = "\n".join(html_parts)

    return full_html, 200, {"Content-Type": "text/html; charset=utf-8"}


# Required for Vercel — must export `app`
# No need to call anything else — Vercel auto-detects `app`
