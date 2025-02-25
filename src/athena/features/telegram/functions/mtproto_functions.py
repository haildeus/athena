from typing import Optional, List
from random import randint

from pyrogram import Client

from pyrogram.raw.base.messages import Chats
from pyrogram.raw.types import (
    InputChannel,
    Channel,
)
from pyrogram.raw.functions.channels import (
    GetInactiveChannels,
    GetChannelRecommendations,
)
from pyrogram.raw.functions.messages import (
    GetDialogFilters,
    GetSuggestedDialogFilters,
    UpdateDialogFilter,
    UpdateDialogFiltersOrder,
)
from pyrogram.raw.functions.contacts import GetTopPeers

from src.athena.core import logger
from src.athena.features.telegram.schemas.mtproto_schemas import (
    CategoryRanking,
    TelegramCommunity,
    Folder,
    FolderBase,
    FolderEdit,
)


def assert_one_true(
    dialogs: bool,
    forward_users: bool,
    forward_chats: bool,
    groups: bool,
    channels: bool,
) -> bool:
    """
    Assert that at least one of the categories is true
    """
    return sum([dialogs, forward_users, forward_chats, groups, channels]) > 0


async def get_top_peers(
    user_client: Client,
    dialogs: bool = False,
    forward_users: bool = False,
    forward_chats: bool = False,
    groups: bool = False,
    channels: bool = False,
):
    """
    Get top peers based on category
    """
    try:
        assert assert_one_true(dialogs, forward_users, forward_chats, groups, channels)
    except AssertionError:
        raise ValueError("At least one category must be true")

    STANDARD_LIMIT = 25
    STANDARD_OFFSET = 0
    STANDARD_HASH = 1

    top_peers_function_call = GetTopPeers(
        offset=STANDARD_OFFSET,
        limit=STANDARD_LIMIT,
        hash=STANDARD_HASH,
        correspondents=dialogs,
        forward_users=forward_users,
        forward_chats=forward_chats,
        groups=groups,
        channels=channels,
    )

    response = await user_client.invoke(top_peers_function_call)
    return response


async def get_and_process_top_peers(
    user_client: Client,
    dialogs: bool = False,
    forward_users: bool = False,
    forward_chats: bool = False,
    groups: bool = False,
    channels: bool = False,
):
    """
    Get top peers and process them
    """
    response = await get_top_peers(
        user_client, dialogs, forward_users, forward_chats, groups, channels
    )
    ranking_obj = CategoryRanking.from_top_peers(response)
    return ranking_obj


async def get_interests_by_visited_channels(user_client: Client):
    """
    Get channels users visits most
    """
    pass


async def get_user_channels(user_client: Client):
    """
    Get all channels users follows
    """
    pass


async def get_active_user_communities(user_client: Client):
    """
    Most messages and most forwards for chats and users
    """
    pass


async def get_user_chats(user_client: Client):
    """
    Get every chat user has
    """
    pass


async def get_inactive_chats_and_channels(user_client: Client):
    """
    Get inactive chats and channels
    """
    pass


async def get_similar_channels(
    user_client: Client, channel: Optional[InputChannel] = None
) -> List[TelegramCommunity]:
    """
    Get similar channels based on similarities of subscribers.
    """
    similar_channels = []

    try:
        get_channel_recommendations_function_call = GetChannelRecommendations(
            channel=channel,
        )

        response = await user_client.invoke(get_channel_recommendations_function_call)
    except Exception as e:
        logger.error(f"Error getting similar channels: {e}")
        return []

    for entry in response.chats:
        try:
            if isinstance(entry, Channel):
                similar_channels.append(TelegramCommunity.from_channel(entry))
        except Exception as e:
            logger.error(f"Error getting similar channels: {e}")
            continue

    return similar_channels


async def get_existing_folders(user_client: Client):
    """
    Get existing folders
    """
    response = await user_client.invoke(GetDialogFilters())
    print(response.filters[0])
    folders = [
        Folder.from_dialog_filter(dialog_filter) for dialog_filter in response.filters
    ]
    return folders


async def get_suggested_folders(user_client: Client):
    """
    Get suggested folders
    """
    response = await user_client.invoke(GetSuggestedDialogFilters())
    return response


async def create_folder(user_client: Client, folder: FolderBase):
    """
    Create a new folder
    """
    folder_id = randint(1, 1000)
    dialog_filter = folder.to_dialog_filter(folder_id)

    if dialog_filter.check_if_all_bool_false():
        raise ValueError("Folder is empty: please add some chats, channels, etc.")

    try:
        update_function_call = UpdateDialogFilter(
            id=folder_id,
            filter=dialog_filter,
        )
        response = await user_client.invoke(update_function_call)
    except Exception as e:
        logger.error(f"Error creating folder: {e}")
        return False

    return True


# TODO: Finish updating folder
async def edit_folder(
    user_client: Client, folder_old: Folder, updated_folder_fields: FolderEdit
):
    """
    Edit existing folder
    """
    pass


async def delete_folder(user_client: Client, folder_id: int):
    """
    Delete existing folder
    """
    delete_function_call = UpdateDialogFilter(id=folder_id)
    try:
        response = await user_client.invoke(delete_function_call)
    except Exception as e:
        logger.error(f"Error deleting folder: {e}")
        return False
    return True


# TODO: Add safe-checks to ensure that the folder_ids are valid
async def new_folder_order(user_client: Client, folder_ids: List[int]):
    """
    Set new folder order
    """
    update_order_function_call = UpdateDialogFiltersOrder(order=folder_ids)
    try:
        response = await user_client.invoke(update_order_function_call)
    except Exception as e:
        logger.error(f"Error updating folder order: {e}")
        return False
    return True
