#  MIT License
#
#  Copyright (c) 2019-present Dan <https://github.com/delivrance>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE

import os
import asyncio
import importlib
import logging
import requests
from pyrogram import Client, filters, idle
from logging.handlers import RotatingFileHandler
from config import API_ID, API_HASH, BOT_TOKEN
from Extractor.modules import ALL_MODULES
from web import web_app
import threading

bot = Client("rg_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

LOGIN_SEND_OTP_URL = "https://theia.rankersgurukul.com/api/v1/user/login/sendOtp"
LOGIN_VERIFY_OTP_URL = "https://theia.rankersgurukul.com/api/v1/user/login/verifyOtp"
MY_COURSES_URL = "https://theia.rankersgurukul.com/api/v1/user/myCourses"
BATCH_CONTENT_URL = "https://theia.rankersgurukul.com/api/v1/batch/{}/contents"

user_tokens = {}

LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("log.txt", maxBytes=5000000, backupCount=10),
        logging.StreamHandler(),
    ],
)

async def sumit_boot():
    for all_module in ALL_MODULES:
        importlib.import_module("Extractor.modules." + all_module)
    LOGGER.info("» BOT DEPLOYED ✅")
    await idle()
    LOGGER.info("» BOT STOPPED.")

def run_web():
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sumit_boot())

# === RG Button Handler (Only Prompt) ===
@bot.on_message(filters.regex("(?i)RG Vikramjeet"))
async def rg_button(_, message):
    await message.reply("Send Id*Password or Token or Phone Number")

# === Input Handler: token / phone / otp ===
@bot.on_message(filters.text & filters.private)
async def handle_login(_, message):
    user_id = message.from_user.id
    text = message.text.strip()

    if "*" in text:
        await message.reply("❌ ID*Password login not supported.")
        return

    if text.startswith("eyJ"):
        user_tokens[user_id] = {"token": text}
        await message.reply("✅ Token saved. Fetching courses...")
        await fetch_and_send_courses(message, text)
        return

    if text.isdigit() and len(text) == 10:
        res = requests.post(LOGIN_SEND_OTP_URL, json={"phone": text})
        if res.ok:
            user_tokens[user_id] = {"phone": text}
            await message.reply("📩 OTP sent! Now send the 6-digit OTP.")
        else:
            await message.reply("❌ Failed to send OTP.")
        return

    if text.isdigit() and len(text) == 6 and user_id in user_tokens:
        phone = user_tokens[user_id].get("phone")
        res = requests.post(LOGIN_VERIFY_OTP_URL, json={"phone": phone, "otp": text})
        if res.ok:
            token = res.json().get("accessToken")
            user_tokens[user_id]["token"] = token
            await message.reply("✅ Logged in! Fetching your courses...")
            await fetch_and_send_courses(message, token)
        else:
            await message.reply("❌ OTP verification failed.")
        return

async def fetch_and_send_courses(message, token):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(MY_COURSES_URL, headers=headers)
    try:
        course_data = res.json()
    except Exception:
        await message.reply("❌ Error decoding response from server. Please try again later.")
        return

    txt_output = []
    for course in course_data:
        title = course.get("batchTitle", "No Title")
        batch_id = course.get("batchId")
        txt_output.append(f"📘 {title}\n")
        content_url = BATCH_CONTENT_URL.format(batch_id)
        res2 = requests.get(content_url, headers=headers)
        if res2.ok:
            for item in res2.json().get("topics", []):
                name = item.get("name", "Untitled")
                url = item.get("videoUrl") or item.get("fileUrl") or "N/A"
                txt_output.append(f"• {name}: {url}")
            txt_output.append("\n")

    txt_path = f"/mnt/data/{message.from_user.id}_rg_courses.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(txt_output))

    await message.reply_document(txt_path, caption="📚 All Paid + Free Batches")

bot.run()
