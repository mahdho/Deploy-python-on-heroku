import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, ConversationHandler

# Enable logging for debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define states for conversation
SELECTING_ACTION, SELECTING_COIN, SENDING_NAME, SENDING_ADDRESS, CONFIRMING_TRANSACTION = range(5)

# Initialize a dictionary to store user data during the conversation
user_data = {}

# Replace with your bot token and owner's user ID
TOKEN = "6627678216:AAHN6K9m9MpWKbooCBv2a6fTXcaW8oDtYvM"
OWNER_USER_ID = "5981331448"

# Start command - provide the user with available commands
def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    if update.callback_query:
        update.callback_query.answer()

    # Welcome message with the user's name
    context.bot.send_message(update.effective_chat.id, f"Welcome, {user.first_name}! This is our bot.")

    if update.effective_chat.type == "private" and context.user_data.get("help_clicked"):
        # Send a video link when "Help" is clicked
        context.bot.send_message(update.effective_chat.id, "Here's a helpful video: https://www.youtube.com/watch?v=xr_D_1fyFFs&list=RDxr_D_1fyFFs&start_radio=1")
    else:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("About", callback_data='about')],
            [InlineKeyboardButton("Payment", callback_data='payment')],
            [InlineKeyboardButton("Help", callback_data='help')],
        ])
        context.bot.send_message(
            update.effective_chat.id,
            text="Here are the available options:",
            reply_markup=reply_markup
        )

    return SELECTING_ACTION

# About command - provide information and images
def about(update: Update, context: CallbackContext) -> int:
    update.callback_query.answer()

    about_text = """
About Us - Flash BTC Sellers

Welcome to Flash BTC Sellers, your trusted source for buying and selling Flash Bitcoin (BTC)! We specialize in providing a secure and efficient platform for cryptocurrency enthusiasts and traders.

Our Mission

At Flash BTC Sellers, our mission is to make cryptocurrency transactions simple and accessible to everyone. We believe in the potential of cryptocurrencies like Flash Bitcoin and aim to facilitate safe and convenient trading experiences for our customers.

Customer Reviews👇🏻👇🏻👇🏻👇🏻👇🏻👇🏻👇🏻
    """
    context.bot.send_message(update.effective_chat.id, about_text, parse_mode='Markdown')

    # Send review photos (replace with actual image URLs)
    review_photos = [
        'https://i.ibb.co/LJ08VWM/11.jpg',
        'https://i.ibb.co/sCtyHtQ/22.jpg',
        'https://i.ibb.co/zrgf8X2/33.jpg',
        'https://i.ibb.co/F3mB6bm/1111.jpg',
        'https://i.ibb.co/syHk1KY/111.jpg',
        'https://i.ibb.co/VVJ91gk/222.jpg',
    ]

    for photo_url in review_photos:
        context.bot.send_photo(update.effective_chat.id, photo=photo_url)

    return SELECTING_ACTION

# Payment command - provide coin selection buttons
def payment(update: Update, context: CallbackContext) -> int:
    update.callback_query.answer()
    user_id = update.effective_user.id

    user_data[user_id] = {'coin': None, 'address': None, 'transaction_pic': None, 'name': None}

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("BTC", callback_data='BTC')],
        [InlineKeyboardButton("USDT", callback_data='USDT')],
        [InlineKeyboardButton("Lite Coin", callback_data='Lite Coin')],
        [InlineKeyboardButton("Binance", callback_data='Binance')],
    ])
    update.callback_query.edit_message_text(
        text="Please select a coin for payment:",
        reply_markup=reply_markup
    )

    return SELECTING_COIN

# Handle coin selection
def select_coin(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    query = update.callback_query
    query.answer()

    coin = query.data
    user_data[user_id]['coin'] = coin

    # Define coin-specific addresses here
    coin_addresses = {
        'BTC': 'Network(Bitcoin)```1LEkUTcRW66kLuKEnhe9Fyd53P4gZpXpvQ```',
        'USDT': 'Network(Ethereum:ERC20)```0x519d5b8ccbd32449dcddcee5307f7569e34cd876```',
        'Lite Coin': 'Network(Litecoin)```LYMKZSUgxUjxAg4ZhUV13oEK6XyW7miodY```',
        'Binance': 'ID```560050915```',
    }

    address = coin_addresses.get(coin, 'Unknown coin')
    user_data[user_id]['address'] = address

    query.edit_message_text(f"You selected {coin}. Here is the {coin} address: {address}\n\nPlease send me your name:")

    return SENDING_NAME

# Handle user's name
def send_name(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    text = update.message.text
    user_data[user_id]['name'] = text

    update.message.reply_text(
        "Please send a picture of the transaction for verification, or type /cancel to cancel."
    )

    return CONFIRMING_TRANSACTION

# Handle transaction photo confirmation
def confirm_transaction(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    user = update.effective_user
    message = update.message

    if message.text.lower() == 'yes':
        if user_id == int(OWNER_USER_ID):
            update.message.reply_text("You cannot confirm your own transaction.")
            return ConversationHandler.END

        # Forward the photo and user details to the owner
        transaction_photo = user_data[user_id]['transaction_pic']
        context.bot.forward_message(int(OWNER_USER_ID), user_id, message.message_id)
        context.bot.send_photo(int(OWNER_USER_ID), photo=transaction_photo.file_id)
        context.bot.send_message(
            int(OWNER_USER_ID),
            f"Transaction details from {user.username} ({user_id}):\n"
            f"Coin: {user_data[user_id]['coin']}\n"
            f"Address: {user_data[user_id]['address']}\n"
            f"Name: {user_data[user_id]['name']}"
        )
        context.bot.send_message(
            user_id,
            "Thank you! We will contact you soon.ASAP🥰 Please Restart Our Bot /start"
        )

    user_data[user_id] = {}
    return ConversationHandler.END

# Cancel the conversation
def cancel(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    user_data[user_id] = {}
    update.message.reply_text("Conversation canceled.")
    return ConversationHandler.END

# Handle transaction photo
def handle_transaction_photo(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    message = update.message

    if message.photo:
        # Handle the photo
        photo = message.photo[-1]  # Get the largest available photo
        user_data[user_id]['transaction_pic'] = photo

        update.message.reply_text(
            "You've sent a transaction photo. Please type 'Yes' or 'No' to confirm the transaction."
        )
    else:
        update.message.reply_text(
            "Please send a picture of the transaction for verification, or type /cancel to cancel."
        )

    return CONFIRMING_TRANSACTION

# Define a handler for regular text messages
def handle_text(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text.lower()
    if user_message in ["hi", "hello", "hey", "hello ummm"]:
        update.message.reply_text("Hello! How can I help you?")
    else:
        update.message.reply_text("馬鹿😑, I don't understand those words.😑")

# Main function to start the bot
def main():
    # Additional print statements
    print("   ▄▄▄       ███▄    █ ▄▄▄█████▓ ▒█████   ███▄    █▓██   ██▓")
    print("   ▒████▄     ██ ▀█   █ ▓  ██▒ ▓▒▒██▒  ██▒ ██ ▀█   █ ▒██  ██▒")
    print("   ▒██  ▀█▄  ▓██  ▀█ ██▒▒ ▓██░ ▒░▒██░  ██▒▓██  ▀█ ██▒ ▒██ ██░")
    print("   ░██▄▄▄▄██ ▓██▒  ▐▌██▒░ ▓██▓ ░ ▒██   ██░▓██▒  ▐▌██▒ ░ ▐██▓░")
    print("    ▓█   ▓██▒▒██░   ▓██░  ▒██▒ ░ ░ ████▓▒░▒██░   ▓██░ ░ ██▒▓░")
    print("    ▒▒   ▓▒█░░ ▒░   ▒ ▒   ▒ ░░   ░ ▒░▒░▒░ ░ ▒░   ▒ ▒   ██▒▒▒ ")
    print("     ▒   ▒▒ ░░ ░░   ▒ ▒░    ░      ░ ▒ ▒░ ░ ░░   ░ ▒░▓██ ░▒░ ")
    print("     ░   ▒      ░   ░ ░   ░      ░ ░ ░ ▒     ░   ░ ░ ▒ ▒ ░░  ")
    print("         ░  ░         ░              ░ ░           ░ ░ ░       ")
    print("                                                     ░ ░      ")

    updater = Updater(token=TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_ACTION: [
                CallbackQueryHandler(about, pattern='^about$'),
                CallbackQueryHandler(payment, pattern='^payment$'),
                CallbackQueryHandler(start, pattern='^help$')
            ],
            SELECTING_COIN: [CallbackQueryHandler(select_coin, pattern='^(BTC|USDT|Lite Coin|Binance)$')],
            SENDING_NAME: [MessageHandler(Filters.text & ~Filters.command, send_name)],
            CONFIRMING_TRANSACTION: [MessageHandler(Filters.text & Filters.regex('^(Yes|No)$'), confirm_transaction)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conversation_handler)
    dispatcher.add_handler(MessageHandler(Filters.photo, handle_transaction_photo))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))  # Add text message handler

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
