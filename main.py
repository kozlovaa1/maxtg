from max import MaxClient as Client
from filters import filters
from classes import Message
from telegram import send_to_telegram
from routing import parse_tg_chat_map, telegram_target_for
import html
import time, os
from dotenv import load_dotenv

load_dotenv()

MAX_TOKEN = os.getenv("MAX_TOKEN")
MAX_CHAT_IDS = [int(x) for x in os.getenv("MAX_CHAT_IDS").split(",")]

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
TG_CHAT_MAP, TG_CHAT_MAP_WARNINGS = parse_tg_chat_map(os.getenv("TG_CHAT_MAP"))
if not MAX_TOKEN or MAX_CHAT_IDS == [] or not TG_BOT_TOKEN or (not TG_CHAT_ID and not TG_CHAT_MAP):
    print("Ошибка в .env, перепроверьтье")
MONITOR_ID = os.getenv("MONITOR_ID")
MONITOR_DEBUG = os.getenv("MONITOR_DEBUG", "").lower() in ("1", "true", "yes", "on")
BOT_NAME = os.getenv("BOT_NAME", os.getenv("HOSTNAME", "maxtg"))
client = Client(MAX_TOKEN)

for warning in TG_CHAT_MAP_WARNINGS:
    print(
        f"[{BOT_NAME}] TG_CHAT_MAP warning: "
        f"entry={warning['position']} reason={warning['reason']}",
        flush=True,
    )

def monitor_event(title: str, text: str = ""):
    title = f"[{BOT_NAME}] {title}"
    print(f"{title}: {text}" if text else title, flush=True)
    if MONITOR_ID:
        body = f"<b>{html.escape(title)}</b>"
        if text:
            body += f"\n<pre>{html.escape(text)}</pre>"
        send_to_telegram(TG_BOT_TOKEN, MONITOR_ID, body)

def monitor_debug(text: str):
    if not MONITOR_DEBUG:
        return
    monitor_event("Max debug", text)

def contact_name(user):
    if not user:
        return "MAX канал"
    if user.contact.names:
        return user.contact.names[0].name
    return str(user.contact.id)

@client.on_connect
def onconnect():
    if client.me != None:
        print(f"Имя: {client.me.contact.names[0].name}, Номер: {client.me.contact.phone} | ID: {client.me.contact.id}")

@client.on_error
def onerror(key: str, text: str):
    monitor_event(f"Max problem: {key}", text)


@client.on_message(filters.any())
def onmessage(client: Client, message: Message):
    tracked = message.chat.id in MAX_CHAT_IDS
    has_sender = message.user is not None
    tg_target = None
    tg_route = "not_applicable"
    if tracked:
        tg_target, tg_route = telegram_target_for(message.chat.id, TG_CHAT_MAP, TG_CHAT_ID)

    if not tracked:
        routing = "ignored_not_in_MAX_CHAT_IDS"
    elif tg_target is None:
        routing = "ignored_no_TG_TARGET"
    elif not has_sender:
        routing = "forward_candidate_no_sender"
    else:
        routing = "forward_candidate"
    monitor_debug(
        "[debug] Max message: "
        f"chat_id={message.chat.id}, "
        f"status={message.status}, "
        f"user_id={message.sender or 'unknown'}, "
        f"has_text={message.text != ''}, "
        f"attaches={len(message.attaches)}, "
        f"tracked={tracked}, "
        f"routing={routing}, "
        f"tg_route={tg_route}, "
        f"tg_target_set={tg_target is not None}"
    )
    if tracked and message.status != "REMOVED":
        if tg_target is None:
            return
        msg_text = message.text or ""
        msg_attaches = message.attaches or []
        name = contact_name(message.user)
        if "link" in message.kwargs.keys():
            if "type" in message.kwargs["link"]:
                if message.kwargs["link"]["type"] == "REPLY": # TODO
                    ...
                if message.kwargs["link"]["type"] == "FORWARD":
                    forwarded_message = message.kwargs["link"].get("message", {})
                    msg_text = forwarded_message.get("text", msg_text) or ""
                    msg_attaches = forwarded_message.get("attaches", msg_attaches) or []
                    forwarded_sender = forwarded_message.get("sender")
                    forwarded_name = "MAX канал"
                    if forwarded_sender:
                        try:
                            forwarded_msg_author = client.get_user(id=forwarded_sender, _f=1)
                            forwarded_name = contact_name(forwarded_msg_author)
                        except Exception as e:
                            print(f"Forwarded author lookup failed: {e}", flush=True)
                    name = f"{name}\n(Переслано: {forwarded_name})"

        if msg_text != "" or msg_attaches != []:
            send_to_telegram(
                TG_BOT_TOKEN,
                tg_target,
                f"<b>{name}</b>\n{msg_text}" if msg_text != "" else f"<b>{name}</b>",
                msg_attaches
                # [attach['baseUrl'] for attach in msg_attaches if 'baseUrl' in attach]
            )
import threading

try:
    client.run()
except Exception as e:
    monitor_event("Max startup failed", str(e))
    raise

threading.Event().wait()
