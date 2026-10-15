from dotenv import load_dotenv
load_dotenv()

import os
import threading
from collections import defaultdict, deque
import requests
from flask import Flask, request

app = Flask(__name__)

# ==== PUT YOUR TOKEN HERE - ONLY 1 PLACE TO EDIT ====
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN") or "EAAUI7UHttGIBSlD9bd0HMDhJoXGZACbUwK5HwexHAuttJ1rbhF4zWQWJl1Tn5nsAQkHmZCkqUMZAavXZAlvKGWFtmQAgYkqSYZChpZBtyNk6J8okTuQqBGdS2YCQX33pYbyvkL64hFyLAMWv6z4IGnBOn5eTHd5ervMu5s2CWZA2LoBu8qsOSvPoGejduZAqqBoex2Bc1W9hLzccwkCoUdZCy7so5QjVloOYZA5ZCqwe4Q9oenWxQZAlRa1NNp7LkzbOvCmQDdEa5o2hva01OLTSrz9UKBxUGG6q0gyGqwZDZD"
PHONE_NUMBER_ID = "1397462873447006"
VERIFY_TOKEN = "talha123"

# FREE AI - No money needed
GROQ_API_KEY = os.getenv("") or "" # Lgsk_BL1EaosSuNNYhpoSUCeEWGdyb3FYsQVbgObBkSMIzDftd43dZtTPeave empty if no money
MODEL = "llama-3.3-70b-versatile"

print(f"TOKEN CHECK: {'YES FOUND - ' + WHATSAPP_TOKEN[:20] + '...' if WHATSAPP_TOKEN and 'PASTE' not in WHATSAPP_TOKEN else 'NO - PLEASE PASTE TOKEN IN CODE'}")
print(f"PHONE ID: {PHONE_NUMBER_ID}")

# ---- Shop Info ----
SHOP_INFO = """
Shop name: Talha Collection
Location: Lahore, near Anarkali
Phone: 03307373599
Products:
- Product A: Rs.1000, black color, most popular
- Product B: Rs.2000, premium quality
"""

SYSTEM_PROMPT = f"""You are Talha, friendly sales assistant of Talha Collection Lahore.

SHOP INFO:
{SHOP_INFO}

HOW TO TALK:
- Roman Urdu / English mix, use "ap"
- Warm, natural shopkeeper, 2-3 lines max
- If bored/sad/love problem, reply like real friend, then gently bring back to shop
- Never say you are AI
"""

# Memory
history = defaultdict(lambda: deque(maxlen=12))
seen_ids = deque(maxlen=500)

def free_ai_reply(number, text):
    # 1. Try FREE Groq if key available
    if GROQ_API_KEY and "PASTE" not in GROQ_API_KEY:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in list(history[number]):
                msgs.append(m)
            msgs.append({"role": "user", "content": text})
            data = {"model": MODEL, "messages": msgs, "temperature": 0.8, "max_tokens": 250}
            r = requests.post(url, headers=headers, json=data, timeout=15)
            if r.status_code == 200:
                reply = r.json()['choices'][0]['message']['content'].strip()
                history[number].append({"role": "user", "content": text})
                history[number].append({"role": "assistant", "content": reply})
                return reply
        except Exception as e:
            print(f"Groq failed: {e}")

    # 2. 100% FREE Local Super Human (No API)
    history[number].append({"role": "user", "content": text})
    msg = text.lower()

    if msg in ["hlo","hi","hello","salam","aoa","aslam o alaikum"]:
        reply = "Wa Alaikum Salam! 😊 Kya haal hai? Main Talha Saab, apki shop se - batao kya chahiye?"
    elif "your name" in msg or "apka name" in msg or "naam" in msg or "who are you" in msg:
        reply = "Main Talha Saab hun! Lahore wali shop ka assistant 😊 Apka naam kya hai?"
    elif "how are you" in msg or "kese ho" in msg or "kya haal" in msg:
        reply = "Alhamdulillah zabardast! Ap sunao kya chal raha hai? 😊"
    elif any(x in msg for x in ["bor","udhas","neend","akela","sad","tired"]):
        reply = "Oho kyu bor ho rahe ho? Chalo main hun na, gup lagate hain! Kya soch rahe ho? 😊"
    elif any(x in msg for x in ["gf","love","dil","pyaar","breakup"]):
        reply = "Ohooo love story! 😍 Batao kya hua? Main sun raha hun!"
    elif any(x in msg for x in ["product","price","kitne","rate"]):
        reply = "Hamare pas 2 zabardast products hain!\n\n🖤 Product A - Rs.1000 (Black, most popular)\n💙 Product B - Rs.2000 (Premium)\n\nKonsa dekhna hai apko?"
    else:
        reply = f"Acha '{text}' 😊 Samajh gaya! Aur batao is bare me kya khayal hai? Shop se kuch chahiye ya bas gup shup karein?"

    history[number].append({"role": "assistant", "content": reply})
    return reply

def send_whatsapp(to, body):
    if not WHATSAPP_TOKEN or "PASTE" in WHATSAPP_TOKEN:
        print("!!! ERROR: Please paste your WHATSAPP_TOKEN in app.py line 11")
        return
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "text": {"body": body}}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        if r.status_code >= 400:
            print(f"WhatsApp Send Error {r.status_code}: {r.text[:300]}")
        else:
            print(f"✅ Sent to {to}: {body[:50]}...")
    except Exception as e:
        print(f"Send failed: {e}")

def handle(number, text):
    print(f"Handling message from {number}: {text}")
    reply = free_ai_reply(number, text)
    send_whatsapp(number, reply)

@app.route("/")
def home():
    return "✅ Talha Bot LIVE - 100% FREE"

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK VERIFIED!")
        return challenge, 200
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    print("\n=== NEW MESSAGE ===")
    try:
        entry = data.get("entry", [])[0] if data.get("entry") else None
        if not entry:
            return "OK", 200
        value = entry.get("changes", [])[0].get("value", {}) if entry.get("changes") else {}
        messages = value.get("messages", [])
        for m in messages:
            if m["id"] in seen_ids:
                continue
            seen_ids.append(m["id"])
            if m.get("type") == "text":
                from_num = m["from"]
                body = m["text"]["body"]
                print(f"From {from_num}: {body}")
                threading.Thread(target=handle, args=(from_num, body), daemon=True).start()
    except Exception as e:
        print(f"Webhook Error: {e}")
        import traceback
        traceback.print_exc()
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))