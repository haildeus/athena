from pyrogram import Client
from pyrogram.types import Sticker
from pyrogram.errors.exceptions.not_acceptable_406 import StickersetInvalid

from src.athena.features.telegram.schemas.stickers_schemas import (
    SUPPORTED_STICKER_SETS,
    StickerFetchResponse,
    StickerUseCase,
    StickerFamiliarityLevel,
)
from src.athena.features.telegram.schemas.telegram_exceptions import StickerFetchError
from src.athena.core import logger


async def get_random_sticker(
    bot_client: Client,
    chat_id: int,
    use_case: StickerUseCase,
    familiarity_level: StickerFamiliarityLevel = None,
) -> Sticker | None:
    """
    Get a random sticker from the supported sticker sets
    """
    try:
        sticker_set = SUPPORTED_STICKER_SETS.get_random_sticker(
            use_case, familiarity_level
        )
    except Exception as e:
        logger.error(f"Error fetching random sticker: {e}")
        raise e
    if not sticker_set:
        logger.error("No sticker set found")
        raise StickerFetchError("No sticker set found")

    set_name = sticker_set.set_name
    sticker = sticker_set.sticker

    try:
        fetched_set = await bot_client.get_stickers(set_name)
    except StickersetInvalid as e:
        logger.error(f"Sticker set {set_name} not found: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error fetching sticker set: {e}")
        raise e

    for sticker in fetched_set:
        if sticker.emoji == sticker_set.sticker:
            return sticker

    return None


async def send_random_sticker(
    bot_client: Client,
    chat_id: int,
    use_case: StickerUseCase,
    familiarity_level: StickerFamiliarityLevel = None,
):
    sticker = await get_random_sticker(bot_client, chat_id, use_case, familiarity_level)
    if not sticker:
        logger.error("No sticker found")
        raise StickerFetchError("No sticker found")
    file_id = sticker.file_id
    await bot_client.send_sticker(chat_id, file_id, caption="Testing")
