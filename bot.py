import os
import requests
import feedparser
import random
from datetime import datetime
from urllib.parse import quote

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL_ID = os.environ["TELEGRAM_CHANNEL_ID"]

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

CATEGORIES = [
    ("🇮🇳 இந்திய செய்திகள்", "India latest news"),
    ("🏦 வங்கி & பொருளாதாரம்", "India banking economy RBI news"),
    ("🌍 சர்வதேச செய்திகள்", "international world news"),
    ("🔬 அறிவியல் & தொழில்நுட்பம்", "science technology news"),
    ("🏛️ அரசு திட்டங்கள்", "India government schemes"),
    ("🏅 விளையாட்டு செய்திகள்", "India sports news"),
    ("📚 கல்வி & தேர்வுகள்", "India education competitive exams"),
    ("💰 நிதி & வணிகம்", "India finance business news"),
]

def get_news(query):
    url = (
        "https://news.google.com/rss/search?q="
        + quote(query)
        + "&hl=ta&gl=IN&ceid=IN:ta"
    )

    feed = feedparser.parse(url)

    news = []

    for item in feed.entries[:10]:
        news.append({
            "title": item.get("title", ""),
            "link": item.get("link", ""),
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

    if not response.json().get("ok"):
        raise Exception("Telegram posting failed")


def post_current_affair():

    category, query = random.choice(CATEGORIES)

    news = get_news(query)

    if not news:
        print("No news found. Skipping post.")
        return

    item = random.choice(news)

    today = datetime.now().strftime("%d-%m-%Y")

    message = f"""
<b>📰 தமிழ் நடப்பு நிகழ்வுகள்</b>

{category}

📅 {today}

━━━━━━━━━━━━━━━━━━

<b>📌 முக்கிய செய்தி:</b>

{item['title']}

━━━━━━━━━━━━━━━━━━

🎯 <b>போட்டித் தேர்வுகளுக்கு முக்கியமானது</b>

இந்த செய்தி SBI, IBPS, RRB, TNPSC மற்றும் பிற போட்டித் தேர்வுகளுக்கான நடப்பு நிகழ்வுகள் பகுதியில் முக்கியத்துவம் வாய்ந்தது.

🔗 <a href="{item['link']}">முழு செய்தியைப் படிக்க</a>

━━━━━━━━━━━━━━━━━━

#CurrentAffairs #TamilCurrentAffairs
#SBI #RRB #IBPS #TNPSC #CompetitiveExams
"""

    send_message(message)

    print("News successfully posted!")


if __name__ == "__main__":
    post_current_affair()
