import os
import sys
import requests
import feedparser
from datetime import datetime
from urllib.parse import quote

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL_ID = os.environ["TELEGRAM_CHANNEL_ID"]

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

CATEGORIES = {
    "morning": [
        "இந்தியா முக்கிய செய்திகள்",
        "Tamil Nadu latest news",
        "India current affairs"
    ],
    "national": [
        "India national news",
        "Government of India schemes",
        "India current affairs"
    ],
    "banking": [
        "RBI banking news India",
        "Indian economy",
        "Banking current affairs"
    ],
    "international": [
        "World news current affairs",
        "International current affairs"
    ]
}

def get_news(query, limit=5):
    url = (
        "https://news.google.com/rss/search?q="
        + quote(query)
        + "&hl=ta&gl=IN&ceid=IN:ta"
    )

    feed = feedparser.parse(url)
    news = []

    for entry in feed.entries[:limit]:
        title = entry.get("title", "")
        link = entry.get("link", "")

        if title:
            news.append({
                "title": title,
                "link": link
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
        raise Exception(result)

    print("Telegram message sent successfully!")


def create_news_post(category):
    queries = CATEGORIES.get(category, [])

    news = []
    seen = set()

    for query in queries:
        items = get_news(query, 5)

        for item in items:
            if item["title"] not in seen:
                seen.add(item["title"])
                news.append(item)

    news = news[:8]

    today = datetime.now().strftime("%d-%m-%Y")

    if category == "morning":
        heading = "🌅 காலை முக்கிய செய்திகள்"
    elif category == "national":
        heading = "🇮🇳 தேசிய நடப்பு நிகழ்வுகள்"
    elif category == "banking":
        heading = "🏦 வங்கி & பொருளாதார செய்திகள்"
    elif category == "international":
        heading = "🌍 சர்வதேச செய்திகள்"
    else:
        heading = "📰 நடப்பு செய்திகள்"

    message = f"<b>{heading}</b>\n"
    message += f"📅 {today}\n\n"

    if not news:
        message += "இன்று செய்திகள் பெற முடியவில்லை. பின்னர் முயற்சிக்கவும்."
    else:
        for i, item in enumerate(news, 1):
            message += f"{i}. {item['title']}\n"
            message += f"🔗 <a href='{item['link']}'>செய்தியை படிக்க</a>\n\n"

    message += "\n#TamilCurrentAffairs #CurrentAffairs #CompetitiveExams"

    send_message(message)


def create_quiz():
    today = datetime.now().strftime("%d-%m-%Y")

    quiz = [
        {
            "question": "இந்தியாவின் மத்திய வங்கி எது?",
            "options": [
                "A) SBI",
                "B) RBI",
                "C) NABARD",
                "D) SEBI"
            ],
            "answer": "B) RBI",
            "explanation": "இந்தியாவின் மத்திய வங்கி Reserve Bank of India."
        },
        {
            "question": "இந்தியாவில் நாணயங்களை வெளியிடும் அதிகாரம் யாருக்கு உள்ளது?",
            "options": [
                "A) SBI",
                "B) Finance Ministry",
                "C) RBI",
                "D) SEBI"
            ],
            "answer": "B) Finance Ministry",
            "explanation": "இந்திய நாணயங்களை இந்திய அரசின் நிதி அமைச்சகம் வெளியிடுகிறது."
        },
        {
            "question": "இந்தியாவின் பங்குச் சந்தை ஒழுங்குமுறை அமைப்பு எது?",
            "options": [
                "A) RBI",
                "B) SEBI",
                "C) NABARD",
                "D) IRDAI"
            ],
            "answer": "B) SEBI",
            "explanation": "SEBI இந்திய பங்குச் சந்தையை ஒழுங்குபடுத்துகிறது."
        }
    ]

    day = datetime.now().day
    q = quiz[day % len(quiz)]

    message = f"<b>📝 தினசரி தேர்வு வினா</b>\n"
    message += f"📅 {today}\n\n"
    message += f"<b>{q['question']}</b>\n\n"

    for option in q["options"]:
        message += option + "\n"

    message += "\n#DailyMCQ #SBI #RRB #CompetitiveExams"

    send_message(message)


if __name__ == "__main__":
    category = sys.argv[1] if len(sys.argv) > 1 else "morning"

    if category == "quiz":
        create_quiz()
    else:
        create_news_post(category)
