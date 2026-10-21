import telebot
from flask import Flask
from threading import Thread

TOKEN = '8944741788:AAE27y2JQD4NZrQN20e1YSe7pjAeikpthG4'
ADMIN_ID = '6367413561' # ID-и худатро нависед!

# 📌 Рӯйхати кодҳо. Ба ҷои ин мисолҳо кодҳои 5-6 рақамаи худро нависед.
# "код": "girl" (барои духтарон) ё "boy" (барои писарон)
VALID_CODES = {
    "54821": "girl",
    "93712": "girl",
    "10493": "girl",
    "73920": "boy",
    "58203": "boy",
    "91045": "boy",
    "50821": "girl",
    "96712": "girl",
    "14593": "girl",
    "78320": "boy",
    "59203": "boy",
    "98445": "boy"
}

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_states = {}

@app.route('/')
def index():
    return "Bot is running!"

@bot.message_handler(commands=['start'])
def start(message):
    user_states[message.chat.id] = {'state': 'waiting_name'}
    bot.send_message(message.chat.id, "Ассалому алайкум! Хуш омадед ба FL STYLE.\n\nЛутфан, ному насаби худро нависед:")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_name')
def get_name(message):
    user_states[message.chat.id]['name'] = message.text
    user_states[message.chat.id]['state'] = 'waiting_phone'
    bot.send_message(message.chat.id, "Ташаккур! Ҳоло рақами телефони худро нависед:")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_phone')
def get_phone(message):
    user_states[message.chat.id]['phone'] = message.text
    user_states[message.chat.id]['state'] = 'waiting_code'
    
    name = user_states[message.chat.id]['name']
    phone = user_states[message.chat.id]['phone']
    
    # Ба ту паём мефиристем
    admin_msg = f"🛍️ ДАРХОСТИ НАВ!\n\n👤 Ном: {name}\n📱 Рақам: {phone}\n\nБарои қабул, ба ӯ яке аз кодҳоро диҳед."
    try:
        bot.send_message(ADMIN_ID, admin_msg)
    except Exception as e:
        print(f"Хато: {e}")
        
    bot.send_message(message.chat.id, "Ташаккур! Дархост қабул шуд. Интизор шавед, ба зудӣ код мегиред.\n\nЛутфан, коди худро ворид кунед:")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_code')
def check_code(message):
    entered_code = message.text.strip() # Рақамҳоро тоза мекунад
    
    if entered_code in VALID_CODES:
        gender = VALID_CODES[entered_code]
        user_states[message.chat.id]['state'] = 'authorized'
        user_states[message.chat.id]['gender'] = gender
        
        if gender == "girl":
            bot.send_message(message.chat.id, "✅ Код қабул шуд! Хуш омадед ба менюи Либосҳои занона.")
        else:
            bot.send_message(message.chat.id, "✅ Код қабул шуд! Хуш омадед ба менюи Либосҳои мардона.")
    else:
        bot.send_message(message.chat.id, "❌ Код хато аст ё вуҷуд надорад! Аз нав кӯшиш кунед.")

def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    t = Thread(target=run_bot)
    t.start()
    app.run(host='0.0.0.0', port=8080)
