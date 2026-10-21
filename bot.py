import telebot
from flask import Flask
from threading import Thread

TOKEN = '8944741788:AAHB-a5ubhmotVqtVGGXxpJ_aAjAlZ0Tj9Q'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Салом! Ман боти мағозаи FL STYLE ҳастам. Ман кор мекунам!")

def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    t = Thread(target=run_bot)
    t.start()
    app.run(host='0.0.0.0', port=8080)
