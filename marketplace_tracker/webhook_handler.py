import requests
import logger
import json
import time
import traceback
import os

accepted_status_codes = [200, 204]

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = "-1004321013556"


def send_webhook(url, data, webhook_send_delay, request_timeout):
    try:
        embed = data.get("embeds", [{}])[0]

        title = embed.get("title", "Nouvelle annonce")
        item_url = embed.get("url", "")
        thumbnail = embed.get("thumbnail", {}).get("url", "")
        fields = embed.get("fields", [])

        price = ""
        if fields:
            price = fields[0].get("name", "")

        message = f"🆕 <b>{title}</b>\n\n💰 {price}\n\n🔗 <a href=\"{item_url}\">Voir l'annonce</a>"

        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

        response = requests.post(
            telegram_url,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            },
            timeout=request_timeout
        )

        if response.status_code == 200:
            return True

        logger.error_log(
            "Telegram error: " + str(response.status_code) + " " + response.text,
            ""
        )
        return False

    except Exception:
        logger.error_log("Telegram webhook failed", traceback.format_exc())
        return False


def send_unhandled_webhook(url, request_timeout, data):
    return