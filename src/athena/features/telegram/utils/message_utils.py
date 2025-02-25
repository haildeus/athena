import asyncio

from pyrogram import enums
from pyrogram.types import InlineKeyboardMarkup, Message


async def streaming_message_helper(
    message: Message,
    text: str,
    parse_mode: enums.ParseMode,
    quote: bool = False,
    disable_web_page_preview: bool = True,
    reply_markup: InlineKeyboardMarkup | None = None,
):
    """
    A function that simulates a streaming response from a model provided a text message

    Params:
        message: The message to send the streaming response to
        text: The text to stream to the user
    """

    if len(text) <= 100:
        await message.reply_text(
            text,
            parse_mode=parse_mode,
            quote=quote,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=reply_markup,
        )
        return

    # reply with the first chunk
    total_message = ""

    initial_message = await message.reply_text(
        text[:100],
        parse_mode=parse_mode,
        quote=quote,
        disable_web_page_preview=disable_web_page_preview,
        reply_markup=reply_markup,
    )
    total_message += text[:100]

    # stream the rest of the text
    chunk_size = 200  # Adjust for optimal appearance/rate limit
    delay = 0.2  # seconds of delay

    for i in range(100, len(text), chunk_size):
        chunk = text[i : i + chunk_size]
        total_message += chunk
        await initial_message.edit_text(
            total_message, parse_mode=parse_mode, reply_markup=reply_markup
        )
        await asyncio.sleep(delay)
