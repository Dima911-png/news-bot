import os, json, re, hashlib, html, time
import requests
import feedparser

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHANNEL = os.getenv("TELEGRAM_CHANNEL_ID", "").strip()
GEMINI = os.getenv("GEMINI_API_KEY", "").strip()
STATE_PATH = "state.json"
MAX_POSTS = 2
FEEDS = [
    "https://news.google.com/rss/search?q=Москва+новости+when:1d&hl=ru&gl=RU&ceid=RU:ru",
    "https://news.google.com/rss/search?q=Москва+транспорт+when:1d&hl=ru&gl=RU&ceid=RU:ru",
]
MOSCOW_WORDS = ("москва", "москве", "москвы", "москвич", "московск", "мкад", "мцд", "мцк")

def clean(s):
    s = re.sub(r"<[^>]*>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()

def state_load():
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"posted": []}

def generate(title, summary, url):
    post = "📰 <b>" + html.escape(title) + "</b>\n\n" + html.escape(summary[:500])
    if GEMINI:
        prompt = "Перепиши новость о Москве кратко по-русски в заголовок и 2 предложения. Не выдумывай факты. Исходник:\n" + title + "\n" + summary[:2500]
        try:
            resp = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                params={"key": GEMINI},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=20
            )
            resp.raise_for_status()
            post = html.escape(resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip())
        except Exception as e:
            print("AI unavailable, using RSS text:", e)
    return post + '\n\n🔗 <a href="' + html.escape(url, quote=True) + '">Источник</a>'

def publish(text):
    response = requests.post(
        "https://api.telegram.org/bot" + TOKEN + "/sendMessage",
        json={"chat_id": CHANNEL, "text": text, "parse_mode": "HTML"},
        timeout=20
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(str(data))

def main():
    if not TOKEN or not CHANNEL:
        raise SystemExit("Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID to GitHub Actions secrets.")
    state = state_load()
    old = set(state.get("posted", []))
    items = []
    for feed_url in FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                title = clean(getattr(entry, "title", ""))
                summary = clean(getattr(entry, "summary", ""))
                link = getattr(entry, "link", "")
                key = hashlib.sha256((getattr(entry, "id", "") or link or title).encode()).hexdigest()
                combined = (title + " " + summary).lower()
                if key not in old and link and any(word in combined for word in MOSCOW_WORDS):
                    items.append((entry, key, title, summary, link))
        except Exception as e:
            print("RSS source error:", e)
    unique = []
    seen = set()
    for item in items:
        if item[1] not in seen:
            seen.add(item[1])
            unique.append(item)
    unique.sort(key=lambda x: getattr(x[0], "published_parsed", None) or time.gmtime(0), reverse=True)
    count = 0
    for entry, key, title, summary, link in unique[:MAX_POSTS]:
        publish(generate(title, summary, link))
        old.add(key)
        count += 1
        print("Published:", title)
        time.sleep(2)
    state["posted"] = list(old)[-1000:]
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    print("Done. Posted", count)

if __name__ == "__main__":
    main()
