import random
import sqlite3
import telebot
from telebot import apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==============================================================================
# НАСТРОЙКИ ПОДКЛЮЧЕНИЯ К СЕРВЕРУ MECHAGRAM
# ==============================================================================
TOKEN = "1780267851:VZ6LFlTpcBcBvl4sLJe7_2HTQ07cLk83dsb"  # Замените на токен от @BotFather[span_8](start_span)[span_8](end_span)
SERVER_URL = "http://177.3.213.27:8081"  # Адрес сервера Mechagram[span_9](start_span)[span_9](end_span)

apihelper.API_URL = f"{SERVER_URL}/bot{{0}}/{{1}}"
apihelper.FILE_URL = f"{SERVER_URL}/file/bot{{0}}/{{1}}"

bot = telebot.TeleBot(TOKEN)

# Данные администратора и каналов/чатов
ADMIN_USERNAME = "arabov"
CHANNEL_LINK = "https://t.me/bbgamesinfo"
CHAT_LINK = "https://t.me/+-bb2qE7EC855hGawfEi9icRq"

# ==============================================================================
# БАЗА ДАННЫХ SQLite
# ==============================================================================
db_conn = sqlite3.connect("players.db", check_same_thread=False)
db_cursor = db_conn.cursor()

db_cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    balance INTEGER,
    bank INTEGER,
    bc INTEGER,
    status TEXT,
    clan TEXT,
    rating INTEGER,
    business TEXT,
    mine TEXT,
    bitcoins INTEGER
)
""")
db_conn.commit()

def get_user(user_id, first_name, username=""):
    db_cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = db_cursor.fetchone()
    
    if row is None:
        db_cursor.execute("""
        INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, first_name, username, 10000, 0, 0, "Игрок", "Отсутствует", 100, "Нет", "Нет", 0))
        db_conn.commit()
        return {
            "name": first_name, "username": username, "balance": 10000,
            "bank": 0, "bc": 0, "status": "Игрок", "clan": "Отсутствует",
            "rating": 100, "business": "Нет", "mine": "Нет", "bitcoins": 0
        }
    else:
        if username:
            db_cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
            db_conn.commit()
        return {
            "name": row[1], "username": row[2], "balance": row[3],
            "bank": row[4], "bc": row[5], "status": row[6], "clan": row[7],
            "rating": row[8], "business": row[9], "mine": row[10], "bitcoins": row[11]
        }

def update_user_field(user_id, field, value):
    db_cursor.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
    db_conn.commit()

# ==============================================================================
# КЛАВИАТУРЫ ГЛАВНОГО МЕНЮ
# ==============================================================================
def main_menu_keyboard(user_id, username):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(text="💡 Основное", callback_data="menu_main"),
        InlineKeyboardButton(text="🎲 Игры", callback_data="menu_games"),
        InlineKeyboardButton(text="💥 Развлекательное", callback_data="menu_fun"),
        InlineKeyboardButton(text="🏰 Кланы", callback_data="menu_clans"),
        InlineKeyboardButton(text="💎 Донат (BB COIN)", callback_data="menu_donate")
    )
    if username and username.lower() == ADMIN_USERNAME.lower():
        kb.add(InlineKeyboardButton(text="🛠 Админ-панель", callback_data="admin_panel"))
    return kb

def back_to_main_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_home"))
    return kb

# ==============================================================================
# АДМИНСКИЕ КОМАНДЫ (ЧЕРЕЗ ЧАТ)
# ==============================================================================
@bot.message_handler(commands=['send'])
def admin_broadcast(message):
    if not message.from_user.username or message.from_user.username.lower() != ADMIN_USERNAME.lower():
        return
    text_to_send = message.text.replace("/send", "").strip()
    if not text_to_send:
        bot.reply_to(message, "❌ Напишите текст: /send Текст")
        return
    db_cursor.execute("SELECT user_id FROM users")
    users = db_cursor.fetchall()
    success = 0
    for u in users:
        try:
            bot.send_message(u[0], text_to_send)
            success += 1
        except:
            pass
    bot.reply_to(message, f"✅ Рассылка завершена! Получили: {success} игроков.")

@bot.message_handler(commands=['give'])
def admin_give_money(message):
    if not message.from_user.username or message.from_user.username.lower() != ADMIN_USERNAME.lower():
        return
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "❌ Пример: `/give ID_или_@username сумма`", parse_mode="Markdown")
        return
    target = args[1].replace("@", "")
    try:
        amount = int(args[2])
    except ValueError:
        return
    if target.isdigit():
        db_cursor.execute("SELECT user_id, balance FROM users WHERE user_id = ?", (int(target),))
    else:
        db_cursor.execute("SELECT user_id, balance FROM users WHERE LOWER(username) = ?", (target.lower(),))
    row = db_cursor.fetchone()
    if row:
        update_user_field(row[0], "balance", row[1] + amount)
        bot.reply_to(message, f"✅ Игроку начислено +{amount} монет!")
    else:
        bot.reply_to(message, "❌ Игрок не найден!")

@bot.message_handler(commands=['givebc'])
def admin_give_bc(message):
    if not message.from_user.username or message.from_user.username.lower() != ADMIN_USERNAME.lower():
        return
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "❌ Пример: `/givebc ID_или_@username сумма`", parse_mode="Markdown")
        return
    target = args[1].replace("@", "")
    try:
        amount = int(args[2])
    except ValueError:
        return
    if target.isdigit():
        db_cursor.execute("SELECT user_id, bc FROM users WHERE user_id = ?", (int(target),))
    else:
        db_cursor.execute("SELECT user_id, bc FROM users WHERE LOWER(username) = ?", (target.lower(),))
    row = db_cursor.fetchone()
    if row:
        update_user_field(row[0], "bc", row[1] + amount)
        bot.reply_to(message, f"✅ Игроку начислено +{amount} BC!")
    else:
        bot.reply_to(message, "❌ Игрок не найден!")

# ==============================================================================
# ПРИВЕТСТВИЕ В ГРУППЕ И /start
# ==============================================================================
@bot.message_handler(content_types=['new_chat_members'])
def make_it_group(message):
    for creator in message.new_chat_members:
        if creator.id == bot.get_me().id:
            text = (
                f"👻 Добро пожаловать на борт, друзья! Меня зовут **SS GAMES**, ваш верный игровой бот.\n\n"
                f"🎮 У меня есть множество интересных команд и игр, чтобы скрасить ваше время, будь вы один или в компании друзей!\n\n"
                f"📡 Наш канал: {CHANNEL_LINK}\n"
                f"💬 Наш чат: {CHAT_LINK}\n"
                f"🆘 По всем вопросам - @{ADMIN_USERNAME}"
            )
            bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['start', 'help'])
def start_command(message):
    user = get_user(message.from_user.id, message.from_user.first_name, message.from_user.username)
    text = (
        f"👻 Добро пожаловать на борт, {user['name']}! Меня зовут **SS GAMES**, твой верный игровой бот.\n\n"
        f"🎮 У меня есть множество интересных команд и игр, чтобы скрасить твоё время, будь ты один или в компании друзей! (Кстати, вместе всегда веселее) 🎃\n\n"
        f"🔍 Познакомиться со всеми моими возможностями ты можешь, введя команду «помощь».\n\n"
        f"📡 Наш канал: {CHANNEL_LINK}\n"
        f"💬 Наш чат: {CHAT_LINK}\n\n"
        f"😈 Не уверен, с чего начать своё приключение?\n"
        f"Присоединяйся к нашему официальному чату: {CHAT_LINK}\n\n"
        f"🆘 По всем вопросам — @{ADMIN_USERNAME}\n\n"
        f"Игрок, выберите категорию:[span_10](start_span)"[span_10](end_span)
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu_keyboard(message.from_user.id, message.from_user.username), parse_mode="Markdown")

# ==============================================================================
# ОБРАБОТЧИК КНОПОК И ВСЕХ РАЗДЕЛОВ
# ==============================================================================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    username = call.from_user.username or ""
    user = get_user(user_id, call.from_user.first_name, username)

    # ГЛАВНОЕ МЕНЮ (КАК НА СКРИНШОТЕ)[span_11](start_span)[span_11](end_span)
    if call.data == "back_home" or call.data == "menu_main":
        text = (
            f"Игрок, выберите категорию:[span_12](start_span)[span_12](end_span)\n"
            f"1️⃣ Основное[span_13](start_span)[span_13](end_span)\n"
            f"2️⃣ Игры[span_14](start_span)[span_14](end_span)\n"
            f"3️⃣ Развлекательное[span_15](start_span)[span_15](end_span)\n"
            f"4️⃣ Кланы[span_16](start_span)[span_16](end_span)\n\n"
            f"👽 Так же у нас есть общая беседа: {CHAT_LINK}\n"
            f"🆘 По всем вопросам - @{ADMIN_USERNAME}"
        )
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton(text="💡 Основное", callback_data="sub_main"),
            InlineKeyboardButton(text="🎲 Игры", callback_data="menu_games"),
            InlineKeyboardButton(text="💥 Развлекательное", callback_data="menu_fun"),
            InlineKeyboardButton(text="🏰 Кланы", callback_data="menu_clans"),
            InlineKeyboardButton(text="💎 Донат-меню", callback_data="menu_donate"),
            InlineKeyboardButton(text="🎁 Ежедневный бонус", callback_data="get_bonus")
        )
        if username.lower() == ADMIN_USERNAME.lower():
            kb.add(InlineKeyboardButton(text="🛠 Админ-панель", callback_data="admin_panel"))

        bot.answer_callback_query(call.id)
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=kb, parse_mode="Markdown")

    # 1. ОСНОВНОЕ (ПОЛНЫЙ СПИСОК СО СКРИНШОТОВ)[span_17](start_span)[span_17](end_span)[span_18](start_span)[span_18](end_span)
    elif call.data == "sub_main":
        text = (
            f"💡 **Игрок, основные команды:**[span_19](start_span)[span_19](end_span)\n\n"
            f"💡 Разное: Профиль, Мой лимит, Рейтинг, Продать рейтинг[span_20](start_span)[span_20](end_span)\n"
            f"🍀 Испытать удачу | ⚡ Энергия | ⛏ Шахта[span_21](start_span)[span_21](end_span)[span_22](start_span)[span_22](end_span)\n"
            f"🚗 Машины | 📱 Телефоны | ✈️ Самолёты | 🛥 Яхты | 🚁 Вертолёты | 🏡 Дома[span_23](start_span)[span_23](end_span)\n"
            f"💵 Б/Баланс: {user['balance']} монет\n"
            f"🏦 Банк: {user['bank']} | Депозит | Инвентарь\n"
            f"🌐 Биткоин курс/купить/продать | 🥇 Биткоины: {user['bitcoins']}\n"
            f"💈 Ежедневный бонус | 🏛 Казна\n"
            f"👑 Статус: {user['status']} | 🏰 Клан: {user['clan']}\n\n"
            f"🆘 По вопросам: @{ADMIN_USERNAME}"
        )
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton(text="⛏ Шахта", callback_data="act_mine"),
            InlineKeyboardButton(text="🎁 Ежедневный бонус", callback_data="get_bonus"),
            InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_home")
        )
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=kb, parse_mode="Markdown")

    # 2. ИГРЫ (ПОЛНЫЙ СПИСОК СО СКРИНШОТОВ)[span_24](start_span)[span_24](end_span)
    elif call.data == "menu_games":
        text = (
            f"🎮 **Игрок, игровые команды:**[span_25](start_span)[span_25](end_span)\n\n"
            f"🎰 Спин [ставка 100]\n"
            f"🎲 Кубик [число] [ставка]\n"
            f"🏀 Баскетбол | 🎯 Дартс | 🎳 Боулинг[span_26](start_span)[span_26](end_span)\n"
            f"📉 Трейд [вверх/вниз] | 💰 Казино | 🃏 Бк | 🎰 Джекпот | 🎡 Рулетка | 🐸 Квак[span_27](start_span)[span_27](end_span)\n\n"
            f"💵 Баланс: {user['balance']} монет"
        )
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton(text="🎰 Спин (100)", callback_data="play_spin"),
            InlineKeyboardButton(text="🎲 Кубик (50)", callback_data="play_dice"),
            InlineKeyboardButton(text="🎯 Дартс", callback_data="play_darts"),
            InlineKeyboardButton(text="🎳 Боулинг", callback_data="play_bowling"),
            InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_home")
        )
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=kb, parse_mode="Markdown")

    # 3. РАЗВЛЕКАТЕЛЬНОЕ (ВСЕ КЕЙСЫ, БИЗНЕСЫ, САДЫ И ЗЕЛЬЯ СО СКРИНШОТОВ)[span_28](start_span)[span_28](end_span)[span_29](start_span)[span_29](end_span)
    elif call.data == "menu_fun":
        text = (
            f"💥 **Игрок, развлекательные команды:**[span_30](start_span)[span_30](end_span)[span_31](start_span)[span_31](end_span)\n\n"
            f"🔮 Шар [фраза] | Выбери | Инфа[span_32](start_span)[span_32](end_span)\n"
            f"💍 Браки: Свадьба, Развод, Мой брак, Браки[span_33](start_span)[span_33](end_span)\n"
            f"📦 Кейсы: Купить кейс, Открыть кейс[span_34](start_span)[span_34](end_span)\n"
            f"💼 Бизнес, Генератор, Майнинг ферма, Карьера[span_35](start_span)[span_35](end_span)[span_36](start_span)[span_36](end_span)\n"
            f"🌳 Денежное дерево, Отель, Сады (полить), Зелья[span_37](start_span)[span_37](end_span)\n\n"
            f"Выберите действие:"
        )
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton(text="📦 Кейсы", callback_data="act_cases"),
            InlineKeyboardButton(text="💼 Бизнес", callback_data="act_biz"),
            InlineKeyboardButton(text="🌳 Дерево", callback_data="act_tree"),
            InlineKeyboardButton(text="🧪 Зелья", callback_data="act_potions"),
            InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_home")
        )
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=kb, parse_mode="Markdown")

    # 4. КЛАНЫ (ВСЕ КОМАНДЫ СО СКРИНШОТОВ)[span_38](start_span)[span_38](end_span)[span_39](start_span)[span_39](end_span)[span_40](start_span)[span_40](end_span)
    elif call.data == "menu_clans":
        text = (
            f"🏰 **Игрок, клановые команды:**[span_41](start_span)[span_41](end_span)[span_42](start_span)[span_42](end_span)\n\n"
            f"💡 Мой клан | 🏆 Клановый топ | ✅ Пригласить / Вступить / Исключить[span_43](start_span)[span_43](end_span)\n"
            f"💰 Казна клана [сумма][span_44](start_span)[span_44](end_span)\n"
            f"⚙️ Создать клан: стоимость 250,000,000,000$[span_45](start_span)[span_45](end_span)[span_46](start_span)[span_46](end_span)\n"
            f"🛠 Настройки: приглашение, кик, ранги, казна, ограбление, война, тип[span_47](start_span)[span_47](end_span)\n"
            f"👑 Управление: изменить название, повысить/понизить, передать главу, удалить[span_48](start_span)[span_48](end_span)[span_49](start_span)[span_49](end_span)\n"
            f"⚔️ Клановые захваты и ограбление казны штата[span_50](start_span)[span_50](end_span)\n\n"
            f"💡 Ваш клан: {user['clan']}"
        )
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(
            InlineKeyboardButton(text="🏰 Создать клан (за 100 BC в донате)", callback_data="menu_donate"),
            InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_home")
        )
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=kb, parse_mode="Markdown")

    # 5. ДОНАТ-МЕНЮ (BB COIN / BC)
    elif call.data == "menu_donate":
        text = (
            f"💎 **ДОНАТ-МАГАЗИН BB COIN (BC)** 💎\n\n"
            f"💰 Твой баланс: **{user['bc']} BC**\n"
            f"🆘 По вопросам: @{ADMIN_USERNAME}"
        )
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(
            InlineKeyboardButton(text="💵 Купить 1,000,000 монет (за 10 BC)", callback_data="buy_money_1"),
            InlineKeyboardButton(text="👑 Элитный статус VIP (за 50 BC)", callback_data="buy_vip"),
            InlineKeyboardButton(text="🏰 Создать клан бесплатно (за 100 BC)", callback_data="buy_clan_pass"),
            InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_home")
        )
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=kb, parse_mode="Markdown")

    # АДМИН-ПАНЕЛЬ В ИНЛАЙН КНОПКАХ
    elif call.data == "admin_panel":
        if username.lower() != ADMIN_USERNAME.lower():
            bot.answer_callback_query(call.id, text="❌ У вас нет доступа!", show_alert=True)
            return
        db_cursor.execute("SELECT COUNT(*) FROM users")
        total_players = db_cursor.fetchone()[0]
        text = (
            f"🛠 **ПАНЕЛЬ АДМИНИСТРАТОРА (@{ADMIN_USERNAME})** 🛠\n\n"
            f"📊 Игроков в базе: **{total_players}**\n\n"
            f"📌 **Команды чата:**\n"
            f"• `/send Текст` — рассылка всем\n"
            f"• `/give ID_или_@username сумма` — монеты\n"
            f"• `/givebc ID_или_@username сумма` — BC"
        )
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(
            InlineKeyboardButton(text="➕ Начислить себе +10,000,000 монет", callback_data="admin_add_money"),
            InlineKeyboardButton(text="💎 Начислить себе +500 BC", callback_data="admin_add_bc"),
            InlineKeyboardButton(text="👑 Дать статус 'Создатель'", callback_data="admin_set_status"),
            InlineKeyboardButton(text="👥 Список игроков", callback_data="admin_list_users"),
            InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_home")
        )
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=kb, parse_mode="Markdown")

    # ДЕЙСТВИЯ АДМИНА КНОПКАМИ
    elif call.data == "admin_add_money" and username.lower() == ADMIN_USERNAME.lower():
        update_user_field(user_id, "balance", user["balance"] + 10000000)
        bot.answer_callback_query(call.id, text="✅ Начислено 10,000,000 монет!", show_alert=True)

    elif call.data == "admin_add_bc" and username.lower() == ADMIN_USERNAME.lower():
        update_user_field(user_id, "bc", user["bc"] + 500)
        bot.answer_callback_query(call.id, text="✅ Начислено 500 BC!", show_alert=True)

    elif call.data == "admin_set_status" and username.lower() == ADMIN_USERNAME.lower():
        update_user_field(user_id, "status", "🛠 СОЗДАТЕЛЬ / АДМИН")
        bot.answer_callback_query(call.id, text="✅ Статус изменен!", show_alert=True)

    elif call.data == "admin_list_users" and username.lower() == ADMIN_USERNAME.lower():
        db_cursor.execute("SELECT user_id, name, username, balance, bc FROM users LIMIT 10")
        rows = db_cursor.fetchall()
        report = "👥 **Последние 10 игроков:**\n\n"
        for r in rows:
            uname = f"@{r[2]}" if r[2] else "нет"
            report += f"• ID: `{r[0]}` | {r[1]} ({uname}) | Монет: {r[3]} | BC: {r[4]}\n"
        bot.answer_callback_query(call.id)
        bot.send_message(call.message
