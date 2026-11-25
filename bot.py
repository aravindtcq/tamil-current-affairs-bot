import os
import requests
import feedparser
import random
import json
import hashlib
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL_ID = os.environ["TELEGRAM_CHANNEL_ID"]

API = f"https://api.telegram.org/bot{BOT_TOKEN}"
HISTORY_FILE = "posted_news.json"

CATEGORIES = [
    ("🇮🇳 தேசிய செய்திகள்", "India latest national news"),
    ("🏦 வங்கி & பொருளாதாரம்", "India RBI banking economy news"),
    ("🌍 சர்வதேச செய்திகள்", "international world news"),
    ("🔬 அறிவியல் & தொழில்நுட்பம்", "science technology news"),
    ("🏛️ அரசு திட்டங்கள்", "India government schemes news"),
    ("🏅 விளையாட்டு செய்திகள்", "India sports news"),
    ("📚 கல்வி செய்திகள்", "India education news"),
    ("💰 வணிக செய்திகள்", "India business financial news"),
]

def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[-500:], f, ensure_ascii=False, indent=2)

def get_news(query):
    url = (
        "https://news.google.com/rss/search?q="
        + quote(query)
        + "&hl=ta&gl=IN&ceid=IN:ta"
    )

    feed = feedparser.parse(url)
    news = []

    for entry in feed.entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "")

        if title and link:
            news.append({
                "title": title,
                "link": link,
                "published": entry.get("published", "")
            })

    return news

def get_image(article_url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            article_url,
            headers=headers,
            timeout=15
        )

        soup = BeautifulSoup(response.text, "html.parser")

        # Open Graph image
        og = soup.find("meta", property="og:image")

        if og and og.get("content"):
            return og["content"]

        # Twitter image
        twitter = soup.find("meta", attrs={"name": "twitter:image"})

        if twitter and twitter.get("content"):
            return twitter["content"]

        # First large image
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")

            if src and src.startswith("http"):
                return src

    except Exception as e:
        print("Image extraction failed:", e)

    return None

def send_text(text):
    response = requests.post(
        f"{API}/sendMessage",
        data={
            "chat_id": CHANNEL_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        },
        timeout=30
    )

    response.raise_for_status()

def send_photo(image_url, caption):
    try:
        response = requests.post(
            f"{API}/sendPhoto",
            data={
                "chat_id": CHANNEL_ID,
                "photo": image_url,
                "caption": caption,
                "parse_mode": "HTML"
            },
            timeout=30
        )

        response.raise_for_status()

        if response.json().get("ok"):
            return True

    except Exception as e:
        print("Photo sending failed:", e)

    return False

def post_current_affair():

    history = load_history()

    category, query = random.choice(CATEGORIES)

    news = get_news(query)

    fresh = []

    for item in news:
        news_hash = hashlib.md5(
            item["title"].lower().encode("utf-8")
        ).hexdigest()

        if news_hash not in history:
            item["hash"] = news_hash
            fresh.append(item)

    if not fresh:
        print("No fresh news. Skipping.")
        return

    item = random.choice(fresh)

    today = datetime.now().strftime("%d-%m-%Y")

    caption = f"""
<b>📰 தமிழ் நடப்பு நிகழ்வுகள்</b>

{category}

📅 {today}

━━━━━━━━━━━━━━━━━━

📌 <b>முக்கிய செய்தி:</b>

{item['title']}

━━━━━━━━━━━━━━━━━━

🎯 <b>போட்டித் தேர்வு முக்கியத்துவம்:</b>

இந்த செய்தி நடப்பு நிகழ்வுகள் பகுதியில் முக்கியமானது.

SBI • IBPS • RRB • TNPSC

━━━━━━━━━━━━━━━━━━

🔗 <a href="{item['link']}">முழு செய்தியைப் படிக்க</a>

#TamilCurrentAffairs #CurrentAffairs
#SBI #RRB #IBPS #TNPSC
"""

    image_url = get_image(item["link"])

    posted = False

    if image_url:
        posted = send_photo(image_url, caption)

    if not posted:
        send_text(caption)

    history.append(item["hash"])
    save_history(history)

    print("Posted successfully!")

if __name__ == "__main__":
    post_current_affair()
