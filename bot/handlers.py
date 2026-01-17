import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from services import user_service, ai_service, vocabulary_service

LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
SCENARIOS = {
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        "<b>engwithpeymar</b> | Professional English Assistant\n\n"
        "To begin your personalized mentor session, please select your CEFR proficiency level:",
        reply_markup = ReplyKeyboardMarkup([LEVELS], one_time_keyboard = True, resize_keyboard = True)
    )

async def set_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    if text in LEVELS:
        user_service.set_user_level(user_id, text)
        await update.message.reply_text(
            f"Configuration complete. Current level: {text}.\n\n"
            "Commands:\n"
            "/word — Word of the Day\n"
            "/quiz — Assessment\n"
            "/practice — Situational simulation\n"
            "/sentence — Analysis & Correction\n"
            "/profile — User Stats & XP\n"
            "/save — Save Last Word\n"
            "/mywords — My Vocabulary\n"
            "/menu — Show this menu\n"
            "Or send any text directly for instant feedback.",
            reply_markup = ReplyKeyboardRemove()
        )
    else:
        await update.message.reply_text(
            "Please select a valid level:",
            reply_markup=ReplyKeyboardMarkup([LEVELS], one_time_keyboard=True, resize_keyboard=True)
        )

async def word_of_the_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    level = user_service.get_user_level(user_id)
    if not level:
        await update.message.reply_text("Please set your level first using /start.")
        return
    await update.message.reply_chat_action("typing")
    content = ai_service.generate_word_of_the_day(level)
    user_service.set_last_generated_word(user_id, content)
    user_service.update_xp(user_id, 10)
    await update.message.reply_markdown(content)

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    level = user_service.get_user_level(user_id)
    if not level:
        await update.message.reply_text("Please set your level first using /start.")
        return

    await update.message.reply_chat_action("typing")
    quiz_data = ai_service.generate_quiz(level)
    if not quiz_data or 'question' not in quiz_data:
        await update.message.reply_text("Sorry, I couldn't generate a quiz at this moment.")
        return

    user_service.set_pending_quiz(user_id, quiz_data)
    message = f"<b>Quiz (Level {level})</b>\n\n{quiz_data['question']}\n\n"
    for opt in quiz_data['options']:
        message += f"{opt}\n"
    keyboard = [["A", "B"], ["C", "D"]]
    await update.message.reply_html(
        message,
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard = True, resize_keyboard = True)
    )

async def practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    level = user_service.get_user_level(user_id)
    if not level:
        await update.message.reply_text("Please set your level first using /start.")
        return

    keyboard = [[s] for s in SCENARIOS.keys()]
    await update.message.reply_html(
        "<b>Situational Practice Sessions</b>\n\n"
        "Select a scenario to begin your immersive practice session with Peymar. "
        "I will act as your interlocutor and provide feedback on your accuracy.",
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard = True, resize_keyboard = True)
    )

async def exit_practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_service.set_active_scenario(user_id, None)
    await update.message.reply_html("Simulation ended. You have returned to the standard mode.", reply_markup = ReplyKeyboardRemove())

async def sentence_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_service.set_active_scenario(user_id, None)
    
    await update.message.reply_html(
        "<b>Linguistic Analysis Mode</b>\n\n"
        "Please send the English sentence or text you wish to analyze. "
        "I will provide a professional correction and a detailed linguistic breakdown of your syntax and vocabulary."
    )

async def save_word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if vocabulary_service.save_last_word(user_id):
        await update.message.reply_text("Word saved to your personal vocabulary! 📚")
    else:
        await update.message.reply_text("No recent word found to save or it's already in your list. Try /word first.")

async def mywords_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = vocabulary_service.format_vocabulary_list(user_id)
    await update.message.reply_html(text)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        "<b>engwithpeymar</b> | Main Menu ☰\n\n"
        "• /word — Word of the Day\n"
        "• /quiz — Assessment\n"
        "• /practice — Situational simulation\n"
        "• /sentence — Analysis & Correction\n"
        "• /profile — User Stats & XP\n"
        "• /save — Save Last Word\n"
        "• /mywords — My Vocabulary\n"
        "• /exit — Stop simulation\n\n"
        "Select a command to proceed."
    )

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats = user_service.get_user_stats(user_id)
    level = user_service.get_user_level(user_id) or "N/A"
    
    await update.message.reply_html(
        f"<b>User Profile: {update.effective_user.first_name}</b>\n\n"
        f"🎓 Level: <b>{level}</b>\n"
        f"✨ XP: <b>{stats['xp']}</b>\n"
        f"📚 Saved Words: <b>{stats['vocab_count']}</b>\n"
        f"🔥 Streak: <b>{stats['streak']} days</b>"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    if text in LEVELS:
        await set_level(update, context)
        return

    pending = user_service.get_pending_quiz(user_id)
    if pending and text.strip().upper() in ["A", "B", "C", "D"]:
        selected = text.strip().upper()
        correct = pending['correct_answer'].upper()
        if selected == correct:
            user_service.update_xp(user_id, 20)
            response = f"<b>Result: Correct (+20 XP)</b>\n\n{pending['explanation']}"
        else:
            response = (
                f"<b>Result: Incorrect</b>\n\n"
                f"Correct answer: <b>{correct}</b>\n\n"
                f"{pending['explanation']}"
            )
            
        user_service.set_pending_quiz(user_id, None)
        await update.message.reply_html(response, reply_markup=ReplyKeyboardRemove())
        return
    level = user_service.get_user_level(user_id)
    if not level:
        await update.message.reply_text("Please select your level first:", 
            reply_markup=ReplyKeyboardMarkup([LEVELS], one_time_keyboard=True, resize_keyboard=True))
        return

    if text in SCENARIOS:
        context_data = {
            "name": text,
            "description": SCENARIOS[text],
            "history": []
        }
        user_service.set_active_scenario(user_id, context_data)
        await update.message.reply_html(
            f"<b>Entering Simulation: {text}</b>\n\n"
            f"<i>{SCENARIOS[text]}</i>\n\n"
            "I will begin. Use /exit to stop the session at any time.\n\n"
            "Peymar: 'Hello! Welcome. How can I assist you today?'",
            reply_markup=ReplyKeyboardRemove()
        )
        context_data["history"].append({"role": "assistant", "content": "Hello! Welcome. How can I assist you today?"})
        user_service.set_active_scenario(user_id, context_data)
        return

    active_scenario = user_service.get_active_scenario(user_id)
    if active_scenario:
        await update.message.reply_chat_action("typing")
        response = ai_service.generate_scenario_response(
            active_scenario["name"],
            active_scenario["history"],
            text,
            level
        )
        active_scenario["history"].append({"role": "user", "content": text})
        active_scenario["history"].append({"role": "assistant", "content": response})
        if len(active_scenario["history"]) > 10:
            active_scenario["history"] = active_scenario["history"][-10:]
        user_service.set_active_scenario(user_id, active_scenario)
        await update.message.reply_text(response)
        return


    await update.message.reply_chat_action("typing") 
    correction = ai_service.correct_sentence(text, level)
    await update.message.reply_markdown(correction)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        "<b>engwithpeymar</b> System Help\n\n"
        "• /start — Profile setup\n"
        "• /word — Daily intelligence\n"
        "• /quiz — Assessment\n"
        "• /practice — Situational simulation\n"
        "• /practice — Situational simulation\n"
        "• /practice — Situational simulation\n"
        "• /practice — Situational simulation\n"
        "• /sentence — Analysis & Correction\n"
        "• /profile — Stats & Levels\n"
        "• /save — Save Word\n"
        "• /mywords — Vocabulary List\n"
        "• /menu — Show Menu\n"
        "• /exit — Stop simulation\n\n"
        "Submit any English text for professional analysis."
    )

