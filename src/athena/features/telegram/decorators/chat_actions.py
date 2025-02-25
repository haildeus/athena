from functools import wraps
from pyrogram import enums
from typing import Optional


def chat_action(action: enums.ChatAction, delay: int = 5):
    def decorator(func):
        @wraps(func)
        async def wrapper(client, message, *args, **kwargs):
            # Access through TelegramClient's instance
            async with client.action_scheduler(
                chat_id=message.chat.id, action=action, delay=delay
            ):
                return await func(client, message, *args, **kwargs)

        return wrapper

    return decorator
