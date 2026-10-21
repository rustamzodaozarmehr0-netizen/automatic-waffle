import telebot

TOKEN = '8944741788:AAHB-a5ubhmotVqtVGGXxpJ_aAjAlZ0Tj9Q'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Салом! Ман боти мағозаи FL STYLE ҳастам. Ман кор мекунам!")

print("Бот кор карда истодааст...")
bot.polling()
