import asyncio
import os
import logging
import sys

from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import Router, F, Bot, Dispatcher
import openai
from config import router, bot, API_TOKEN, OPENAI_API_KEY

# Initializing logging
logging.basicConfig(level=logging.INFO)
openai.api_key = OPENAI_API_KEY

# Initialize bot and dispatcher


async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    openai.api_key = OPENAI_API_KEY
    await dp.start_polling(bot)


@router.message(CommandStart())
async def ask_language(message: Message):
    languages = ["Ukrainian", "Russian", "English"]
    buttons = [InlineKeyboardButton(text=lang, callback_data=lang.lower()) for lang in languages]
    markup = InlineKeyboardMarkup(inline_keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)])
    await message.reply("Please select a language for transcription:", reply_markup=markup)


# This function will handle the user's language choice
@router.callback_query(lambda c: c.data in ["ukrainian", "russian", "english"])
async def set_language(callback_query: CallbackQuery):
    # Here you can set the language for transcription based on the user's choice
    # For demonstration purposes, I'm just sending a message back to the user
    await bot.send_message(callback_query.from_user.id, f"You selected {callback_query.data.capitalize()}!")
    await bot.send_message(callback_query.from_user.id, "Now, please send me a voice message to transcribe.")


@router.message(F.voice)
async def handle_voice(message: Message):
    try:
        # Get the file information
        file_info = await bot.get_file(message.voice.file_id)
        file_path = file_info.file_path

        # Define a temporary file path
        temp_file_path = f"temp_{file_info.file_unique_id}.ogg"

        # Download the voice message to the temporary file
        await bot.download_file(file_path=file_path, destination=temp_file_path)

        # Transcribe the voice message using OpenAI's Whisper API
        with open(temp_file_path, "rb") as audio_file:
            response = openai.Audio.transcribe("whisper-1", audio_file)
            transcript = response['text']

        # Delete the temporary file
        os.remove(temp_file_path)

        # Send the transcription back to the user
        await message.reply(f"Transcription: {transcript}")

    except Exception as e:
        await message.answer(f"An error occurred: {e}")


@router.message(~F.voice)  # This will match all messages that are NOT voice messages
async def handle_non_voice(message: Message):
    await message.reply("Please send a voice message for transcription.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
