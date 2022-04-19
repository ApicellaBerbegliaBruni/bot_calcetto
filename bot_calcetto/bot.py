import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Dispatcher,
    Updater,
)

import env
import logging


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


def delete_match(update: Update, context: CallbackContext):
    """
    update.message.reply_text(
        'provaprova'
    )
    """
    keyboard = [[]]

    chat_data = context.chat_data

    # take current user
    current_user = update.message.from_user["username"]

    if chat_data is not None:
        current_matches = chat_data.get("current_matches", [])
        for match in current_matches:
            if match["manager"] == current_user:
                print(match.get("date"))
                keyboard[0].append(
                    InlineKeyboardButton(
                        "Partita",
                        callback_data='{"players": match["players"],"manager": match["manager"]}',
                    )
                )

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "Quale partita vuoi eliminare?", reply_markup=reply_markup
        )
    else:
        update.message.reply_text("provaprova")


def button_delete(update: Update, context: CallbackContext):
    update.message.reply_text("Risposta")


if __name__ == "__main__":

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    logger = logging.getLogger(__name__)

    # Create the Updater and pass it your bot's token.
    updater = Updater(token=env.BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher: Dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler("partite", matches))
    dispatcher.add_handler(CommandHandler("cancella_partita", delete_match))
    dispatcher.add_handler(CallbackQueryHandler(button_delete))

    # Start the Bot
    updater.start_webhook(
        listen="0.0.0.0",
        port=int(env.PORT),
        url_path=env.BOT_TOKEN,
        webhook_url=f"https://{env.APP_NAME}.herokuapp.com/{env.BOT_TOKEN}",
    )
    # Block until you press Ctrl-C
    updater.idle()
