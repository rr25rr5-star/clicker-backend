from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo
from flask import Flask, request, jsonify
import os
import asyncio

API_TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

app = Flask(__name__)
users_data = {}

# /start komandasi
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            "Play Clicker", web_app=WebAppInfo(url="https://rr25rr5-star.github.io/clicker-miniapp/")
        )
    )
    await message.answer("Clicker o‘yiningizni boshlang!", reply_markup=keyboard)

# Telegram webhook endpoint
@app.route(f"/webhook/{API_TOKEN}", methods=["POST"])
def webhook():
    update = types.Update(**request.json)
    asyncio.run(dp.process_update(update))
    return "OK", 200

# Mini App backend
@app.route("/update", methods=["POST"])
def update():
    data = request.json
    user_id = str(data["user_id"])
    coins_add = data.get("coins_add", 0)
    progress_change = data.get("progress_change", 0)

    if user_id not in users_data:
        users_data[user_id] = {"coins": 0, "progress": 1000, "multiplier": 1}

    users_data[user_id]["coins"] += coins_add * users_data[user_id]["multiplier"]
    users_data[user_id]["progress"] += progress_change
    users_data[user_id]["progress"] = max(0, min(users_data[user_id]["progress"], 1000))

    return jsonify(users_data[user_id])

@app.route("/leaderboard")
def leaderboard():
    sorted_users = sorted(users_data.items(), key=lambda x: x[1]["coins"], reverse=True)
    return jsonify([{ "user_id": k, **v } for k,v in sorted_users])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
