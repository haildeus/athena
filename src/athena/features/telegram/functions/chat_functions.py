from typing import List
from datetime import datetime, timedelta

from pyrogram import Client
from pyrogram.enums import ChatAction, ChatType
from pyrogram.types import Message

from src.athena.features.telegram.schemas.telegram_schemas import (
    ResolvedPeerInfo,
    ChatMessage,
)
from src.athena.core import diskcache, logger


async def send_typing_action(client: Client, chat_id: int):
    """
    Send typing action
    """
    await client.send_chat_action(chat_id, ChatAction.TYPING)


async def resolve_peer_id_for_summary(
    user_client: Client, peer_id: int
) -> ResolvedPeerInfo:
    """
    Resolve peer ID for summary
    """
    resolved_peer = await user_client.get_chat(peer_id)
    peer_type = resolved_peer.type

    if resolved_peer.usernames is not None and len(resolved_peer.usernames) > 0:
        username = resolved_peer.usernames[0].username
    elif resolved_peer.username is not None:
        username = resolved_peer.username
    else:
        username = None

    return ResolvedPeerInfo(
        peer_id=resolved_peer.id,
        peer_name=resolved_peer.title or resolved_peer.first_name,
        peer_username=username,
        peer_type=peer_type,
    )


@diskcache(cache_owner_path="peer_id")
async def fetch_messages_from_last_x_hours(
    user_client: Client, peer_id: int, hours: int
) -> List[ChatMessage]:
    """
    Fetch messages from last X hours
    """
    chunk_size = 1000
    counter = 0
    min_counter = 100

    try:
        message_generator = user_client.get_chat_history(peer_id, limit=chunk_size)
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        raise e

    message_array = []
    time_now = datetime.now()
    time_hours_ago = time_now - timedelta(hours=hours)

    async for message in message_generator:
        if message.date < time_hours_ago and counter > min_counter:
            break
        if message.text is None:
            continue

        chat_message_object = ChatMessage.extract_chat_message_info(message)

        if chat_message_object is None or chat_message_object.message is None:
            continue

        message_array.append(chat_message_object)
        counter += 1

    return message_array


async def fetch_last_x_messages_from_peer(
    user_client: Client, peer_id: int, message_limit: int
) -> List[ChatMessage]:
    """
    Fetch last X messages from peer
    """
    message_generator = user_client.get_chat_history(peer_id, limit=message_limit)
    message_array = []

    async for message in message_generator:
        if message.text is None:
            continue

        chat_message_object = ChatMessage.extract_chat_message_info(message)

        # TODO: Add non-text message processing
        if chat_message_object is None or chat_message_object.message is None:
            continue

        message_array.append(chat_message_object)

    return message_array
