import asyncio
from datetime import datetime
from typing import Optional, Union
from pyrogram import Client
from pyrogram.raw import functions, types
from src.athena.core.system import logger


async def fetch_recent_draft_athena_mentions(
    user_client: Client, username: str, within_minutes: int = 5
) -> Optional[int]:
    """
    Fetch the peer ID of the most recent mention of a username in draft messages

    Args:
        user_client: Authenticated user client
        username: Target username to monitor
        within_minutes: Lookback window in minutes

    Returns:
        Peer ID of the mention, or None if no mention is found
    """
    try:
        # Get all drafts via raw API
        drafts = await user_client.invoke(functions.messages.GetAllDrafts())

        # Calculate time threshold
        time_limit = datetime.now().timestamp() - (within_minutes * 60)

        for update in getattr(drafts, "updates", []):
            # Validate update type and time
            if not (
                isinstance(update, types.UpdateDraftMessage)
                and update.draft.date > time_limit
            ):
                continue

            # Extract peer information
            peer = update.peer
            peer_id = _extract_peer_id(peer)
            if not peer_id:
                continue

            # Check message content
            draft_text = update.draft.message.lower()

            if draft_text.startswith(username):
                return peer_id

        return None

    except Exception as e:
        logger.error(f"Failed to fetch mentions: {str(e)}")
        return None


async def wait_until_fresh_mention_found(
    user_client: Client, username: str, within_minutes: int = 5
) -> Optional[int]:
    no_mention_found = True
    attempts = 0

    while no_mention_found and attempts < 5:
        mention = await fetch_recent_draft_athena_mentions(
            user_client, username, within_minutes
        )
        if mention:
            return mention
        else:
            await asyncio.sleep(1)
            attempts += 1

    return None


def _extract_peer_id(
    peer: types.PeerUser | types.PeerChat | types.PeerChannel,
) -> Optional[int]:
    """Extract ID from different peer types"""
    if isinstance(peer, types.PeerUser):
        return peer.user_id
    if isinstance(peer, types.PeerChat):
        return -peer.chat_id
    if isinstance(peer, types.PeerChannel):
        return int(f"-100{peer.channel_id}")

    return None
