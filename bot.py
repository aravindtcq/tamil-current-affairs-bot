import os
import requests
import feedparser
import random
import json
import hashlib
from datetime import datetime
from urllib.parse import quote

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL_ID = os.environ["TELEGRAM_CHANNEL_ID"]

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
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

    for item in feed.entries:
        title = item.get("title", "").strip()
        link = item.get("link", "")

        if title and link:
            news.append({
                "title": title,
                "link": link,
                "published": item.get("published", "")
            })

    return news

def send_message(text):
    response = requests.post(
        TELEGRAM_URL,
        data={
            "chat_id": CHANNEL_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        },
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    if not result.get("ok"):
        raise Exception(f"Telegram API error: {result}")

def create_exam_point(category, title):
    return f"""
🎯 <b>போட்டித் தேர்வு முக்கியத்துவம்:</b>

இந்த செய்தி நடப்பு நிகழ்வுகள் பகுதியில் முக்கியமானது.
SBI, IBPS, RRB, TNPSC தேர்வுகளில் தொடர்புடைய கேள்விகள் வர வாய்ப்புள்ளது.
"""

def post_current_affair():

    history = load_history()

    category, query = random.choice(CATEGORIES)

    news = get_news(query)

    if not news:
        print("News unavailable. Skipping.")
        return

    # Duplicate prevention
    fresh_news = []

    for item in news:
        news_hash = hashlib.md5(
            item["title"].lower().encode("utf-8")
        ).hexdigest()

        if news_hash not in history:
            item["hash"] = news_hash
            fresh_news.append(item)

    if not fresh_news:
        print("All available news already posted. Skipping.")
        return

    item = random.choice(fresh_news)

    today = datetime.now().strftime("%d-%m-%Y")

    message = f"""
<b>📰 தமிழ் நடப்பு நிகழ்வுகள்</b>

{category}

📅 <b>தேதி:</b> {today}

━━━━━━━━━━━━━━━━━━

📌 <b>முக்கிய செய்தி:</b>

{item['title']}

━━━━━━━━━━━━━━━━━━

📝 <b>செய்தியின் முக்கியத்துவம்:</b>

இந்த நிகழ்வு இந்தியா மற்றும் உலக அளவில் முக்கியத்துவம் வாய்ந்த நடப்பு நிகழ்வாகும்.

இந்த செய்தியின் பின்னணி மற்றும் தொடர்புடைய தகவல்களை போட்டித் தேர்வுகளுக்கு தயாராகும் மாணவர்கள் தெரிந்து வைத்திருக்க வேண்டும்.

━━━━━━━━━━━━━━━━━━

🎯 <b>தேர்வுக்கு முக்கியம்:</b>

SBI • IBPS • RRB • TNPSC

━━━━━━━━━━━━━━━━━━

🔗 <a href="{item['link']}">முழு செய்தியைப் படிக்க</a>

#TamilCurrentAffairs #CurrentAffairs
#SBI #RRB #IBPS #TNPSC #ExamPreparation
"""

    send_message(message)

    history.append(item["hash"])
    save_history(history)

    print("News posted successfully!")

if __name__ == "__main__":
    post_current_affair()
