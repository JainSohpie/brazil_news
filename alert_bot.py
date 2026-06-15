import feedparser
import requests
import json
import os

# ── 설정 (GitHub Secrets에서 불러옴) ──────────────────
RSS_URL   = os.environ["RSS_URL"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID   = os.environ["CHAT_ID"]
SENT_FILE = "sent.json"
# ──────────────────────────────────────────────────────

def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_sent(sent):
    with open(SENT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(sent), f, ensure_ascii=False, indent=2)

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    r = requests.post(url, data=payload)
    r.raise_for_status()

def main():
    sent = load_sent()
    feed = feedparser.parse(RSS_URL)

    new_count = 0
    for entry in feed.entries:
        article_id = entry.get("id", entry.get("link", ""))
        if article_id in sent:
            continue  # 이미 보낸 기사 → 건너뛰기

        title = entry.get("title", "(제목 없음)")
        link  = entry.get("link", "")

        message = f"📰 <b>{title}</b>\n\n{link}"
        send_telegram(message)

        sent.add(article_id)
        new_count += 1

    save_sent(sent)
    print(f"✅ 새 기사 {new_count}개 발송 완료")

if __name__ == "__main__":
    main()
