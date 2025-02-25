import asyncio

from pyrogram.handlers import InlineQueryHandler, MessageHandler, CallbackQueryHandler
from pyrogram import enums, Client, filters
from pyrogram.types import Message, InlineQuery, CallbackQuery

# inline keyboard
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from src.athena.core.system import logger

from src.athena.features.telegram.decorators import chat_action
from src.athena.features.telegram.functions.fetch_athena_inline_origin import (
    fetch_recent_draft_athena_mentions,
)
from src.athena.features.telegram.functions.chat_functions import (
    resolve_peer_id_for_summary,
    fetch_last_x_messages_from_peer,
)
from src.athena.features.telegram.functions.start_functions import process_start_command


async def handle_start_command(bot_client: Client, message: Message):
    """Handle /start command with security checks and interactive response"""
    try:
        # Handle summary parameter
        await process_start_command(bot_client.deus_instance, message)
    except Exception as e:
        logger.error(f"Start command error: {str(e)}")
        await message.reply("❌ An error occurred. Please try again later.")


async def handle_inline_query(bot_client: Client, inline_query: InlineQuery):
    # Store original chat context
    user_id = inline_query.from_user.id
    await bot_client.answer_inline_query(
        inline_query.id,
        results=[],
        switch_pm_text="Get Chat Summary",
        switch_pm_parameter=f"summary_{user_id}",
    )


async def handle_chosen_inline_query(bot_client: Client, chosen_inline_result):
    print(f"Chosen Inline Query: {chosen_inline_result}")


async def handle_callback_query(bot_client: Client, callback_query: CallbackQuery):
    """Handle callback queries from inline keyboard buttons"""
    try:
        # Get the callback data
        data = callback_query.data

        # Answer the callback query to remove loading state
        print(f"Callback query data: {data}")

        await callback_query.answer("https://www.google.com/", show_alert=True)

    except Exception as e:
        logger.error(f"Callback query error: {str(e)}")
        await callback_query.message.reply(
            "❌ An error occurred processing your request"
        )


def register_bot_handlers(client: Client):
    client.add_handler(
        MessageHandler(handle_start_command, filters.command("start") & filters.private)
    )
    client.add_handler(InlineQueryHandler(handle_inline_query))
    client.add_handler(CallbackQueryHandler(handle_callback_query))
