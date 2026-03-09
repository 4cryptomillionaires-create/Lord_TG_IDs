import requests
import time
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_updates(offset=None):
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    r = requests.get(f"{BASE_URL}/getUpdates", params=params)
    return r.json()

def send_message(chat_id, text, reply_to_message_id=None):
    data = {"chat_id": chat_id, "text": text}
    if reply_to_message_id:
        data["reply_to_message_id"] = reply_to_message_id
    requests.post(f"{BASE_URL}/sendMessage", data=data)

offset = None

while True:
    data = get_updates(offset)

    if data.get("ok"):
        for update in data.get("result", []):
            offset = update["update_id"] + 1

            message = update.get("message")
            if not message:
                continue

            chat = message["chat"]
            chat_id = chat["id"]
            message_id = message["message_id"]
            text = message.get("text", "")
            user = message.get("from", {})
            user_id = user.get("id")

            if text == "/start":
                reply = (
                    "Telegram ID Scanner\n\n"
                    "/myid - show your ID\n"
                    "/groupid - show group ID\n"
                    "/id - reply to user to get their ID"
                )

            elif text == "/myid":
                reply = f"Your User ID\n{user_id}"

            elif text == "/groupid":
                group_name = chat.get("title", "Unknown")
                group_id = str(chat.get("id")).replace("-", "")
                group_type = chat.get("type", "Unknown").title()

                members = requests.get(
                    f"{BASE_URL}/getChatMemberCount",
                    params={"chat_id": chat['id']}
                ).json()

                member_count = members.get("result", "Unknown")

                reply = (
                    f"Group Info\n\n"
                    f"Name: {group_name}\n"
                    f"ID: {group_id}\n"
                    f"Type: {group_type}\n"
                    f"Members: {member_count}"
                )

            elif text == "/id" and "reply_to_message" in message:
                target = message["reply_to_message"]["from"]
                name = target.get("first_name", "User")
                reply = f"{name} User ID\n{target['id']}"

            else:
                continue

            send_message(chat_id, reply, message_id)

    time.sleep(1)
