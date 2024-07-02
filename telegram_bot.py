#!/usr/bin/env python
import json
import logging
import os
import shutil
import sys
import pathlib

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

BLENDER_PATH = '/Applications/Blender.app/Contents/MacOS/Blender'
LOCAL_DB = pathlib.Path('./user_database').resolve()
DEFAULT_CONFIG = pathlib.Path('./config.json').resolve()
STATOR_PY = pathlib.Path('./gen_stator.py').resolve()
ROTOR_PY = pathlib.Path('./gen_rotor.py').resolve()

STATOR_CMD = f'{BLENDER_PATH} --background --python {STATOR_PY}'
ROTOR_CMD = f'{BLENDER_PATH} --background --python {ROTOR_PY}'

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def get_user_path(user) -> pathlib.Path:
    user_path = LOCAL_DB / f'USER_{user.id}'
    return user_path


def check_and_save_user_data(user):
    user_path = get_user_path(user)
    if not user_path.exists():
        user_path.mkdir(parents=True)
        config_path = user_path / 'config.json'
        shutil.copyfile(DEFAULT_CONFIG, config_path)


def gen_stator(user):
    root = os.getcwd()
    user_path = get_user_path(user)
    stator_file = user_path / 'stator.stl'
    os.chdir(user_path)
    os.system(STATOR_CMD)
    os.chdir(root)
    return stator_file


def gen_rotor(user):
    root = os.getcwd()
    user_path = get_user_path(user)
    rotor_file = user_path / 'rotor.stl'
    os.chdir(user_path)
    os.system(ROTOR_CMD)
    os.chdir(root)
    return rotor_file


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    check_and_save_user_data(user)
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def other_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Check if configure
    new_config_str = update.message.text.split('\n')
    if new_config_str[0] != 'CONFIGURATION':
        await update.message.reply_text("Unknown input!")
        return
    new_config = { }
    for inputs in new_config_str[1:]:
        key, value = inputs.split(' : ')
        new_config[key] = value
    config_path = get_user_path(update.effective_user) / 'config.json'
    config = { }
    with open(config_path, 'r') as CONFIG:
        config = json.load(CONFIG)
    diff = set(new_config.keys()) - set(config.keys())
    if diff:
        await update.message.reply_text("Unknown input, extra config provided!")
        return
    failed = False
    for key, value in new_config.items():
        try:
            new_config[key] = type(config[key])(value)
        except Exception as er:
            failed = True
            await update.message.reply_text(f'Wrong value provided for {key}, need {type(config[key])}')
    if failed:
        return
    for key, value in new_config.items():
        config[key] = new_config[key]
    with open(config_path, 'w') as CONFIG:
        json.dump(config, CONFIG, indent=True)
    await update.message.reply_text("Config successfully updated!")


async def configure_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    config_path = get_user_path(update.effective_user) / 'config.json'
    config_str = 'CONFIGURATION\n'
    with open(config_path, 'r') as CONFIG:
        config = json.load(CONFIG)
        for key, value in config.items():
            config_str += f'{key} : {value}\n'
    await update.message.reply_text(config_str)
    await update.message.reply_text('Please copy and modify above configuration and resend it if you want to change it!')


async def rotor_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    rotor_file = gen_rotor(update.effective_user)
    document = open(rotor_file, 'rb')
    await context.bot.send_document(update.message.chat_id, document)


async def stator_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    stator_file = gen_stator(update.effective_user)
    document = open(stator_file, 'rb')
    await context.bot.send_document(update.message.chat_id, document)


async def all_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await rotor_command(update, context)
    await stator_command(update, context)


def main(token) -> None:
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("configure", configure_command))
    application.add_handler(CommandHandler("rotor", rotor_command))
    application.add_handler(CommandHandler("stator", stator_command))
    application.add_handler(CommandHandler("all", all_command))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, other_command))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main(sys.argv[1])
