from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import numpy as np
from pydantic import BaseModel, Field, model_validator
from pyrogram.enums import ChatType, MessageEntityType, MessageMediaType
from pyrogram.types import Message

from src.athena.core import logger
from src.athena.core.deus.schemas import Persona


class ResolvedPeerInfo(BaseModel):
    peer_id: int = Field(..., description="ID of the entity")
    peer_name: str = Field(..., description="Title or username of the entity")
    peer_username: str | None = Field(None, description="Username of the entity")
    peer_type: ChatType = Field(..., description="Type of the entity")

    is_private: bool = Field(False, description="Whether the entity is private")

    @model_validator(mode="before")
    def validate_peer_type(cls, values):
        peer_type = values.get("peer_type")
        peer_username = values.get("peer_username")

        if peer_type in [ChatType.PRIVATE, ChatType.BOT] or peer_username is None:
            values["is_private"] = True

        return values

    def deep_link_exists(self) -> bool:
        if self.peer_type in [ChatType.PRIVATE, ChatType.BOT]:
            return False
        return True

    def get_deep_link(self) -> str:
        if self.is_private:
            peer_id = self.peer_id
            if self.peer_type in [ChatType.CHANNEL, ChatType.SUPERGROUP]:
                peer_id = int(str(peer_id)[3:])
            elif peer_id < 0:
                peer_id = abs(peer_id)
            return f"https://t.me/c/{peer_id}"

        else:
            return f"https://t.me/{self.peer_username}"

    def get_button_link(self) -> str:
        if self.is_private:
            peer_id = self.peer_id
            if self.peer_type in [ChatType.CHANNEL, ChatType.SUPERGROUP]:
                peer_id = int(str(peer_id)[3:])
            elif peer_id < 0:
                peer_id = abs(peer_id)
            return f"https://t.me/c/{peer_id}"
        else:
            return f"https://t.me/{self.peer_username}"

    def get_button_text(self) -> str:
        if self.peer_username is None and self.peer_name is None:
            return "Back to chat"

        if self.peer_type in [ChatType.PRIVATE, ChatType.BOT]:
            return f"Back to chat with {self.peer_name}"

        return f"Back to {self.peer_name}"

    def get_entity_name(self) -> str:
        if self.peer_username is None and self.peer_name is None:
            return "Chat"
        else:
            return self.peer_name or self.peer_username

    def get_hyperlink(self) -> str:
        button_link = self.get_button_link()
        entity_name = self.get_entity_name()

        return f"<a href='{button_link}'>{entity_name}</a>"


class ChatMessage(BaseModel):
    message_id: int = Field(..., description="ID of the message")
    first_name: str | None = Field(None, description="First name of the sender")
    username: str | None = Field(None, description="Username of the sender")
    message: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Timestamp of the message")

    # Link preview
    link_preview_title: str | None = Field(
        None, description="Title of the link preview"
    )
    link_preview_description: str | None = Field(
        None, description="Description of the link preview"
    )

    # Negative scores
    is_self: bool = Field(False, description="Whether the message is from the user")
    is_bot: bool = Field(False, description="Whether the message is from a bot")

    # Positive scores
    is_premium: bool = Field(
        False, description="Whether the message is from a premium user"
    )
    is_contact: bool = Field(False, description="Whether the message is from a contact")

    has_mention: bool = Field(
        False, description="Whether the message mentions the user"
    )
    has_link: bool = Field(False, description="Whether the message has a link")

    reaction_count: int = Field(0, description="Number of reactions on the message")
    media_score: int = Field(0, description="Score of the media in the message")

    @property
    def engagement_score(self) -> float:
        """
        Calculate the engagement score of the message
        """
        # --- 1. Feature Preparation (with non-linear transformations) ---

        # Length (using log1p for a smoother curve)
        link_title_length = (
            len(self.link_preview_title) if self.link_preview_title else 0
        )
        link_description_length = (
            len(self.link_preview_description) if self.link_preview_description else 0
        )
        combined_message_length = (
            len(self.message) + link_title_length + link_description_length
        )
        length_score = np.log1p(combined_message_length)

        # Penalize VERY short messages, but still allow for reasonably short ones.
        if combined_message_length < 20:  # Less than ~5 words
            length_score = 0.1  # Small, but non-zero
        else:
            length_score = np.log1p(combined_message_length) / 5.0  # Scale down the log
            length_score = min(length_score, 1.0)  # Limit maximum

        # Reactions (using a modified sigmoid - sharper increase initially)
        reaction_score = 1 / (
            1 + np.exp(-(self.reaction_count - 1) / 2)
        )  # Shift and scale

        # --- 2. Feature Engineering (Interaction Terms) ---
        # TODO: Add later -- it's not that important rn

        # --- 3. Weighted Sum (Weights Optimized for Conversation Importance) ---
        score = (
            0.3 * length_score  # Moderate weight on length (substance)
            - 5.0 * float(self.is_self)  # STRONG penalty for self-messages
            - 3.0 * float(self.is_bot)  # Strong penalty for bot messages (usually)
            + 1.0 * reaction_score  # HIGH weight on reactions (discussion indicator)
            + 0.2
            * float(
                self.is_premium
            )  # Small bonus for premium users (might have higher status)
            + 0.1
            * float(self.is_contact)  # Slight bonus for contacts (more likely relevant)
            + 0.1
            * float(
                self.has_mention
            )  # Small bonus for mentions (targeted conversation)
            + 0.4
            * float(self.has_link)  # Moderate bonus for links (potential information)
            + 0.5 * self.media_score  # Moderate weight on media score (if available)
        )

        # --- 4. Normalization (Min-Max, with adjusted bounds) ---
        # We'll adjust the bounds to reflect the new weights and penalties.
        MIN_SCORE = -5.0  # is_self = True is the main negative driver
        MAX_SCORE = 3.0  # Assuming good length, reactions, and maybe media/link.
        normalized_score = (score - MIN_SCORE) / (MAX_SCORE - MIN_SCORE)

        # Clip to 0-1 range, but favor higher scores.
        normalized_score = np.clip(normalized_score, 0.0, 1.0)

        return normalized_score

    @classmethod
    def extract_chat_message_info(cls, message_object: Message):
        try:
            message_id = message_object.id
            # We don't handle non-text messages yet
            message = message_object.text
            first_name = message_object.from_user.first_name
            username = message_object.from_user.username
            timestamp = message_object.date

            if message_object.web_page is not None:
                link_preview_title = message_object.web_page.title
                link_preview_description = message_object.web_page.description
            else:
                link_preview_title = None
                link_preview_description = None

            if message_object.from_user is not None:
                is_self = message_object.from_user.is_self
                is_bot = message_object.from_user.is_bot
                is_premium = message_object.from_user.is_premium
                is_contact = message_object.from_user.is_contact
            else:
                is_self = False
                is_bot = False
                is_premium = False
                is_contact = False

            if message_object.media is not None:
                if message_object.media == MessageMediaType.DOCUMENT:
                    media_score = 1
                elif message_object.media == MessageMediaType.PHOTO:
                    media_score = 2
                elif message_object.media == MessageMediaType.VIDEO:
                    media_score = 3
                elif message_object.media == MessageMediaType.AUDIO:
                    media_score = 4
                else:
                    media_score = 0
            else:
                media_score = 0

            has_mention = False
            has_link = False
            if message_object.entities is not None:
                for entity in message_object.entities:
                    if entity.type == MessageEntityType.MENTION:
                        has_mention = True
                    if entity.type == MessageEntityType.URL:
                        has_link = True

            reaction_count = 0
            if message_object.reactions is not None:
                for reaction in message_object.reactions.reactions:
                    reaction_count += reaction.count

            return cls(
                message_id=message_id,
                first_name=first_name,
                username=username,
                message=message,
                timestamp=timestamp,
                link_preview_title=link_preview_title,
                link_preview_description=link_preview_description,
                is_self=is_self,
                is_bot=is_bot,
                is_premium=is_premium,
                is_contact=is_contact,
                has_mention=has_mention,
                has_link=has_link,
                reaction_count=reaction_count,
                media_score=media_score,
            )
        except Exception as e:
            logger.error(f"Error extracting chat message info: {e}")
            return None


class ChatMessageReduced(BaseModel):
    txt_id: int = Field(..., description="ID of the message")
    who: str | None = Field(None, description="Who sent the message")
    txt: str = Field(..., description="Message content")
    username: str | None = Field(None, description="Username of the sender")
    eng_score: float = Field(..., description="Engagement score of the message")

    @classmethod
    def from_chat_message(cls, message: ChatMessage):
        return cls(
            txt_id=message.message_id,
            who=message.first_name,
            txt=message.message,
            username=message.username,
            eng_score=message.engagement_score,
        )


class ChatMessageReducedCluster(BaseModel):
    messages: list[ChatMessageReduced] = Field(..., description="List of messages")
    cluster_id: int = Field(..., description="ID of the cluster")


class CommandTypes(Enum):
    SUMMARY = "summary"
    ELSE = "else"


@dataclass
class SummaryDependency:
    persona: Persona


class Summary(BaseModel):
    topic_name: str = Field(..., description="Name of the topic")
    summary: str = Field(
        ..., description="Summary of the topic. One sentence per topic."
    )
    message_ids: list[str] = Field(..., description="Message ids")

    def __str__(self):
        return (
            f"• **{self.topic_name}**: {self.summary} [{', '.join(self.message_ids)}]"
        )


class SumResp(BaseModel):
    topics: list[Summary] = Field(
        ...,
        description="Summaries of the topics (max 5)",
    )

    def to_string(self) -> str:
        return "\n".join(str(topic) for topic in self.topics)


class FollowUpQuestion(BaseModel):
    question: str = Field(..., description="Follow-up question")
    index: int = Field(..., description="Index of the question")


class FollowUpResp(BaseModel):
    questions: list[FollowUpQuestion] = Field(..., description="Follow-up questions")

    def to_string(self) -> str:
        return "\n".join(str(question) for question in self.questions)


class MessageEffects(Enum):
    FIRE = 5104841245755180586
    THUMBS_UP = 5107584321108051014
    HEART = 5159385139981059251
    PARTY = 5046509860389126442
    NEGATIVE = 5104858069142078462
    POOP = 5046589136895476101
