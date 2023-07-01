from config import *
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import g4f
from rich.console import Console
from rich.markdown import Markdown

MODEL = 'gpt-3.5-turbo'
providers = [
    g4f.Provider.Forefront,
    g4f.Provider.GetGpt,
    g4f.Provider.Lockchat
]

print('Starting up bot...')

messages = {}
def handle_response(text, id):
    messages[id].append({"role": "user", "content": text})
    # Reduce conversation size to avoid API Token quantity error
    for provider in providers:
        response = g4f.ChatCompletion.create(model='gpt-3.5-turbo', provider=provider, messages=messages[id][-5:], stream=False)
        if response: break
    messages[id].append({"role": "system", "content": response})
    return response

# Lets us use the /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages.update({update.message.chat.id:[]})
    await update.message.reply_text('Hello there! I\'m a TeleGPT bot. What\'s up?')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id not in messages:
        messages.update({update.message.chat.id:[]})
    # Get basic info of the incoming message
    message_type: str = update.message.chat.type
    text: str = update.message.text

    # Print a log for debugging
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    # React to group messages only if users mention the bot directly
    if message_type == 'group':
        # Replace with your bot username
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text, update.message.chat.id)
        else:
            return  # We don't want the bot respond if it's not mentioned in the group
    else:
        response: str = handle_response(text, update.message.chat.id)

    # Reply normal if the message is in private
    print('Bot:', response)
    await update.message.reply_text(response)

# Log errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

# Run the program
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    # Log all errors
    app.add_error_handler(error)

    print('Polling...')
    # Run the bot
    app.run_polling(poll_interval=5)