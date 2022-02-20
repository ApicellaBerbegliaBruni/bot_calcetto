import json
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Dispatcher,
    Updater,
)


def start(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton(
                "Calcetto (5 vs 5)",
                callback_data='{"new_match_players": "10"}',
            ),
            InlineKeyboardButton(
                "Calciotto (8 vs 8)",
                callback_data='{"new_match_players": "16"}',
            ),
        ],
        [
            InlineKeyboardButton(
                "Calcio (11 vs 11)",
                callback_data='{"new_match_players": "22"}',
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "Che tipo di partita è?", reply_markup=reply_markup
    )


def matches(update: Update, context: CallbackContext):
    chat_data = context.chat_data
    if chat_data is not None:
        current_matches = chat_data.get("current_matches", [])

        for i, match in enumerate(current_matches):
            update.message.reply_text(
                f"Partita {i + 1}:\n"
                f'Organizzatore: @{match["manager"]}\n'
                f'Giocatori: {match["players"]}\n'
                f'Data: {match.get("date", "Da definire")}\n'
                f'Ora: {match.get("time", "Da definire")}\n'
                f'Luogo: {match.get("place", "Da definire")}\n'
                f'Prezzo a persona: {match.get("price", "Da definire")}'
            )


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    query.answer()

    query_data = json.loads(query.data)

    if "new_match_players" in query_data:
        players = query_data["new_match_players"]

        chat_data = context.chat_data
        if chat_data is not None:
            new_match = {
                "players": players,
                "manager": query.from_user.username,
            }
            current_matches = chat_data.get("current_matches", [])
            chat_data["current_matches"] = current_matches + [new_match]

            query.edit_message_text(
                text=f"Creata partita da {players} giocatori!"
            )


if __name__ == "__main__":
    updater = Updater(token=os.getenv("BOT_TOKEN"))
    dispatcher: Dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler("partite", matches))

    updater.start_polling()
    updater.idle()
