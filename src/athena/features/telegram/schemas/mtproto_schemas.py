from typing import Optional, List, Union
from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field
from pyrogram.raw.types.contacts import TopPeers
from pyrogram.raw.base import TopPeerCategory
from pyrogram.raw.types import (
    User,
    Chat,
    Channel,
    TopPeerCategoryChannels,
    TopPeerCategoryCorrespondents,
    TopPeerCategoryForwardChats,
    TopPeerCategoryForwardUsers,
    TopPeerCategoryGroups,
    TopPeerCategoryPeers,
    PeerChannel,
    PeerChat,
    PeerUser,
    InputPeerChannel,
    InputPeerChat,
    InputPeerUser,
    DialogFilter,
    DialogFilterChatlist,
    DialogFilterDefault,
    TextWithEntities,
)

from src.athena.core import logger


class TelegramUser(BaseModel):
    user_id: int = Field(..., description="User ID")

    username: Optional[str] = Field(None, description="Username")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")

    contact: Optional[bool] = Field(False, description="User is a contact")
    mutual_contact: Optional[bool] = Field(
        False, description="User is a mutual contact"
    )

    premium: Optional[bool] = Field(False, description="User is a premium user")
    lang_code: Optional[str] = Field(None, description="Language code")

    is_bot: bool = Field(False, description="User is a bot")

    @classmethod
    def from_user(cls, user: User) -> "TelegramUser":
        user_id = user.id

        if user.usernames is not None and len(user.usernames) > 0:
            username = user.usernames[0].username
        elif user.username is not None:
            username = user.username
        else:
            username = None

        first_name = user.first_name if user.first_name is not None else None
        last_name = user.last_name if user.last_name is not None else None
        contact = user.contact if user.contact is not None else False
        mutual_contact = (
            user.mutual_contact if user.mutual_contact is not None else False
        )
        premium = user.premium if user.premium is not None else False
        lang_code = user.lang_code if user.lang_code is not None else None

        return cls(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            contact=contact,
            mutual_contact=mutual_contact,
            premium=premium,
            lang_code=lang_code,
        )


class TelegramGroupChat(BaseModel):
    group_id: int = Field(..., description="Group ID")
    title: str = Field(..., description="Title")

    created_at: datetime = Field(..., description="Creation date")
    is_creator: bool = Field(False, description="User is the creator of the group")

    participants_count: int = Field(..., description="Number of participants")

    @classmethod
    def from_chat(cls, chat: Chat) -> "TelegramGroupChat":
        group_id = chat.id
        title = chat.title
        participants_count = chat.participants_count

        created_at = datetime.fromtimestamp(chat.date)
        is_creator = chat.creator if chat.creator is not None else False

        return cls(
            group_id=group_id,
            title=title,
            created_at=created_at,
            is_creator=is_creator,
            participants_count=participants_count,
        )


class TelegramCommunity(BaseModel):
    community_id: int = Field(..., description="Community ID")
    title: str = Field(..., description="Title")
    username: Optional[str] = Field(None, description="Username")

    is_channel: bool = Field(False, description="Community is a channel")
    is_supergroup: bool = Field(False, description="Community is a supergroup")
    is_gigagroup: bool = Field(False, description="Community is a gigagroup")
    is_forum: bool = Field(False, description="Community is a forum")

    created_at: datetime = Field(..., description="Creation date")
    is_creator: bool = Field(False, description="User is the creator of the community")

    participants_count: int = Field(..., description="Number of participants")

    @classmethod
    def from_channel(cls, channel: Channel) -> "TelegramCommunity":
        community_id = channel.id
        title = channel.title
        participants_count = channel.participants_count

        if channel.usernames is not None and len(channel.usernames) > 0:
            username = channel.usernames[0].username
        elif channel.username is not None:
            username = channel.username
        else:
            username = None

        is_channel = channel.broadcast if channel.broadcast is not None else False
        is_supergroup = channel.megagroup if channel.megagroup is not None else False
        is_gigagroup = channel.gigagroup if channel.gigagroup is not None else False
        is_forum = channel.forum if channel.forum is not None else False

        created_at = datetime.fromtimestamp(channel.date)
        is_creator = channel.creator if channel.creator is not None else False

        return cls(
            community_id=community_id,
            title=title,
            username=username,
            is_channel=is_channel,
            is_supergroup=is_supergroup,
            is_gigagroup=is_gigagroup,
            is_forum=is_forum,
            created_at=created_at,
            is_creator=is_creator,
            participants_count=participants_count,
        )


class TopPeerUser(TelegramUser):
    rating: float = Field(0, description="Rating")


class TopPeerChat(TelegramGroupChat):
    rating: float = Field(0, description="Rating")


class TopPeerChannel(TelegramCommunity):
    rating: float = Field(0, description="Rating")


class SupportedCategories(Enum):
    POPULAR_CHANNELS = "popular_channels"
    POPULAR_GROUPS = "popular_groups"
    POPULAR_DIALOGS = "popular_dialogs"
    POPULAR_FORWARD_CHATS = "popular_forward_chats"
    POPULAR_FORWARD_USERS = "popular_forward_users"

    @classmethod
    def from_category(cls, category: TopPeerCategory) -> "SupportedCategories":
        if category == TopPeerCategoryChannels:
            return cls.POPULAR_CHANNELS
        elif category == TopPeerCategoryGroups:
            return cls.POPULAR_GROUPS
        elif category == TopPeerCategoryCorrespondents:
            return cls.POPULAR_DIALOGS
        elif category == TopPeerCategoryForwardChats:
            return cls.POPULAR_FORWARD_CHATS
        elif category == TopPeerCategoryForwardUsers:
            return cls.POPULAR_FORWARD_USERS
        else:
            raise ValueError(f"Unsupported category: {category}")


class CategoryEntry(BaseModel):
    category: SupportedCategories = Field(..., description="Category")
    total: int = Field(0, description="Total number of peers in the category")
    peers: List[Union[TopPeerChannel, TopPeerChat, TopPeerUser]] = Field(
        [], description="Peers in the category"
    )


class CategoryRanking(BaseModel):
    popular_channels: Optional[CategoryEntry] = Field(
        None, description="Popular channels"
    )
    popular_groups: Optional[CategoryEntry] = Field(
        None, description="Most popular groups"
    )
    popular_dialogs: Optional[CategoryEntry] = Field(
        None, description="Most frequent 1x1 chats"
    )

    popular_forward_chats: Optional[CategoryEntry] = Field(
        None, description="Most popular chats to forward to"
    )
    popular_forward_users: Optional[CategoryEntry] = Field(
        None, description="Most popular users to forward to"
    )

    def __str__(self):
        return self.model_dump_json(exclude_none=True, exclude_unset=True)

    @classmethod
    def from_top_peers(cls, top_peers: TopPeers) -> "CategoryRanking":
        """
        Process TopPeers and transform Pyrogram objects into pydantic objects
        """

        def get_chat_by_id(
            top_peers: TopPeers, chat_id: int, rating: float
        ) -> TopPeerChat | TopPeerChannel | None:
            """
            Helper function to find chats/channels among top peers
            """
            chats = top_peers.chats
            try:
                for entry in chats:
                    if entry.id == chat_id:
                        return_obj = None
                        if isinstance(entry, Channel):
                            return_obj = TopPeerChannel.from_channel(entry)
                        elif isinstance(entry, Chat):
                            return_obj = TopPeerChat.from_chat(entry)
                        return_obj.rating = rating
                        return return_obj
                    else:
                        continue
                return None
            except Exception as e:
                print(entry)
                logger.error(f"Error getting chat by id: {e}")
                return None

        def get_user_by_id(
            top_peers: TopPeers, user_id: int, rating: float
        ) -> TopPeerUser | None:
            """
            Helper function to find users among top peers
            """
            users = top_peers.users
            try:
                for entry in users:
                    if isinstance(entry, User) and entry.id == user_id:
                        return_obj = TopPeerUser.from_user(entry)
                        return_obj.rating = rating
                        return return_obj
                return None
            except Exception as e:
                print(entry)
                logger.error(f"Error getting user by id: {e}")
                return None

        categories = top_peers.categories

        popular_channels = []
        popular_groups = []
        popular_dialogs = []
        popular_forward_chats = []
        popular_forward_users = []

        for entry in categories:
            print(entry)
            entry: TopPeerCategoryPeers = entry  # for LSP
            category_type = type(entry.category)
            total = entry.count

            for peer in entry.peers:
                rating = peer.rating

                peer_id = peer.peer.user_id or peer.peer.chat_id or peer.peer.channel_id
                try:
                    if category_type == TopPeerCategoryChannels:
                        channel = get_chat_by_id(top_peers, peer_id, rating)
                        if channel is not None:
                            popular_channels.append(channel)

                    elif category_type in [
                        TopPeerCategoryCorrespondents,
                        TopPeerCategoryForwardUsers,
                    ]:
                        user = get_user_by_id(top_peers, peer_id, rating)
                        print(user)
                        if user is not None:
                            if category_type == TopPeerCategoryCorrespondents:
                                popular_dialogs.append(user)
                            elif category_type == TopPeerCategoryForwardUsers:
                                popular_forward_users.append(user)

                    elif category_type in [
                        TopPeerCategoryGroups,
                        TopPeerCategoryForwardChats,
                    ]:
                        chat = get_chat_by_id(top_peers, peer_id, rating)
                        if chat is not None:
                            if category_type == TopPeerCategoryGroups:
                                popular_groups.append(chat)
                            elif category_type == TopPeerCategoryForwardChats:
                                popular_forward_chats.append(chat)
                except Exception as e:
                    print(peer)
                    logger.error(f"Error processing peer: {e}")
                    continue

        popular_channels = CategoryEntry(
            category=SupportedCategories.from_category(category_type),
            total=total,
            peers=popular_channels,
        )
        popular_groups = CategoryEntry(
            category=SupportedCategories.from_category(category_type),
            total=total,
            peers=popular_groups,
        )
        popular_dialogs = CategoryEntry(
            category=SupportedCategories.from_category(category_type),
            total=total,
            peers=popular_dialogs,
        )
        popular_forward_chats = CategoryEntry(
            category=SupportedCategories.from_category(category_type),
            total=total,
            peers=popular_forward_chats,
        )
        popular_forward_users = CategoryEntry(
            category=SupportedCategories.from_category(category_type),
            total=total,
            peers=popular_forward_users,
        )

        return cls(
            popular_channels=popular_channels,
            popular_groups=popular_groups,
            popular_dialogs=popular_dialogs,
            popular_forward_chats=popular_forward_chats,
            popular_forward_users=popular_forward_users,
        )


class FolderPinned(BaseModel):
    pinned: bool = Field(False, description="Pinned")


class FolderPeerChat(FolderPinned):
    chat_id: int = Field(..., description="Chat ID")


class FolderPeerChannel(FolderPinned):
    channel_id: int = Field(..., description="Channel ID")


class FolderPeerUser(FolderPinned):
    user_id: int = Field(..., description="User ID")


class FolderBase(BaseModel):
    folder_title: str = Field(..., description="Title", max_length=12)
    contacts: bool = Field(False, description="Contacts")
    non_contacts: bool = Field(False, description="Non-contacts")
    groups: bool = Field(False, description="Groups")
    channels: bool = Field(False, description="Channels")
    bots: bool = Field(False, description="Bots")
    exclude_muted: bool = Field(False, description="Exclude muted")
    exclude_read: bool = Field(False, description="Exclude read")
    exclude_archived: bool = Field(False, description="Exclude archived")

    emoticon: Optional[str] = Field(None, description="Emoticon")
    no_animate: bool = Field(False, description="No animate")

    @classmethod
    def to_dialog_filter(cls, folder_id: int) -> DialogFilter:
        """
        Convert a FolderBase object to a DialogFilter object
        """
        return DialogFilter(
            id=folder_id,
            title=TextWithEntities(text=cls.folder_title, entities=[]),
            include_peers=[],
            pinned_peers=[],
            contacts=cls.contacts,
            non_contacts=cls.non_contacts,
            groups=cls.groups,
            channels=cls.channels,
            bots=cls.bots,
            exclude_muted=cls.exclude_muted,
            exclude_read=cls.exclude_read,
            exclude_archived=cls.exclude_archived,
            emoticon=cls.emoticon,
            no_animate=cls.no_animate,
        )

    def check_if_all_bool_false(self):
        """
        Helper function to avoid creating empty folders
        """
        return all(
            [
                self.contacts,
                self.non_contacts,
                self.groups,
                self.channels,
                self.bots,
                self.exclude_muted,
                self.exclude_read,
                self.exclude_archived,
                self.no_animate,
            ]
        )


class Folder(FolderBase):
    folder_id: int = Field(..., description="Folder ID")

    include_peers: List[FolderPeerChat | FolderPeerChannel | FolderPeerUser] = Field(
        [], description="Included peers in the folder"
    )
    pinned_peers: List[FolderPeerChat | FolderPeerChannel | FolderPeerUser] = Field(
        [], description="Pinned peers in the folder"
    )

    @classmethod
    def from_dialog_filter(
        cls, dialog_filter: DialogFilter | DialogFilterChatlist | DialogFilterDefault
    ) -> "Folder":
        """
        Process a DialogFilter and transform Pyrogram objects into pydantic objects
        """

        def get_entry(
            peers: List[InputPeerChat | InputPeerChannel | InputPeerUser],
            pinned: bool = False,
        ) -> List[FolderPeerChat | FolderPeerChannel | FolderPeerUser]:
            """
            Helper function to get a peer from a list of peers
            """
            return_array = []
            if peers is None:
                return return_array

            for peer in peers:
                if isinstance(peer, InputPeerChat):
                    return_array.append(
                        FolderPeerChat(chat_id=peer.chat_id, pinned=pinned)
                    )
                elif isinstance(peer, InputPeerChannel):
                    return_array.append(
                        FolderPeerChannel(channel_id=peer.channel_id, pinned=pinned)
                    )
                elif isinstance(peer, InputPeerUser):
                    return_array.append(
                        FolderPeerUser(user_id=peer.user_id, pinned=pinned)
                    )
            return return_array

        if isinstance(dialog_filter, DialogFilterDefault):
            return cls(
                folder_id=0,
                folder_title="Default",
                included_peers=[],
                pinned_peers=[],
            )
        else:
            return_obj = {
                "folder_id": dialog_filter.id,
                "folder_title": dialog_filter.title.text,
                "included_peers": get_entry(dialog_filter.include_peers, pinned=False),
                "pinned_peers": get_entry(dialog_filter.pinned_peers, pinned=True),
            }

            if isinstance(dialog_filter, DialogFilterChatlist):
                return cls(**return_obj)
            elif isinstance(dialog_filter, DialogFilter):
                additional_fields = {
                    "contacts": dialog_filter.contacts,
                    "non_contacts": dialog_filter.non_contacts,
                    "groups": dialog_filter.groups,
                    "channels": dialog_filter.broadcasts,
                    "bots": dialog_filter.bots,
                    "exclude_muted": dialog_filter.exclude_muted,
                    "exclude_read": dialog_filter.exclude_read,
                    "exclude_archived": dialog_filter.exclude_archived,
                    "emoticon": dialog_filter.emoticon,
                    "no_animate": dialog_filter.title_noanimate,
                }
                return cls(**return_obj, **additional_fields)


class FolderEdit(BaseModel):
    folder_title: Optional[str] = Field(None, description="Title", max_length=12)

    contacts: Optional[bool] = Field(None, description="Contacts")
    non_contacts: Optional[bool] = Field(None, description="Non-contacts")
    groups: Optional[bool] = Field(None, description="Groups")
    channels: Optional[bool] = Field(None, description="Channels")
    bots: Optional[bool] = Field(None, description="Bots")

    exclude_muted: Optional[bool] = Field(None, description="Exclude muted")
    exclude_read: Optional[bool] = Field(None, description="Exclude read")
    exclude_archived: Optional[bool] = Field(None, description="Exclude archived")

    emoticon: Optional[str] = Field(None, description="Emoticon")
    no_animate: Optional[bool] = Field(None, description="No animate")
