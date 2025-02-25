import asyncio

from pyrogram import enums
from pyrogram.types import Message

from src.athena.core import diskcache, logger
from src.athena.core.deus.base.base_abstract import DeusAbstract
from src.athena.features.telegram.functions.chat_functions import (
    fetch_messages_from_last_x_hours,
    resolve_peer_id_for_summary,
)
from src.athena.features.telegram.functions.fetch_athena_inline_origin import (
    wait_until_fresh_mention_found,
)
from src.athena.features.telegram.schemas.telegram_schemas import (
    CommandTypes,
    FollowUpResp,
    MessageEffects,
    ResolvedPeerInfo,
    SumResp,
)
from src.athena.features.telegram.utils.variance_utils import (
    community_found_response,
    community_start_response,
    community_summary,
)


async def resolve_start_command(message: Message) -> CommandTypes:
    """
    Process start commands
    """
    if len(message.command) > 1 and message.command[1].startswith("summary"):
        return CommandTypes.SUMMARY
    else:
        return CommandTypes.ELSE


async def process_start_command(deity: DeusAbstract, message: Message):
    """
    Handle start command
    """

    command_type = await resolve_start_command(message)

    if command_type == CommandTypes.SUMMARY:
        return await community_summary_response(deity, message)
    elif command_type == CommandTypes.ELSE:
        return await bot_start_response(deity, message)


async def bot_start_response(deity: DeusAbstract, message: Message):
    """
    Handle bot start response
    """
    from src.athena.core.deus.base.base_instance import Deus

    # Type hinting for LSP
    deity: Deus = deity
    await message.reply(deity.get_telegram_welcome_message())


async def community_summary_response(deity: DeusAbstract, message: Message):
    """Process summary start parameter"""
    from src.athena.core.deus.base.base_instance import Deus

    # Type hinting for LSP
    deity: Deus = deity

    client_object = deity.get_client("TELEGRAM_USER")
    bot_object = deity.get_client("TELEGRAM_BOT")

    username = client_object.get_first_name_short()
    telegram_id = client_object.get_telegram_id()

    user_client = client_object.get_client_object()
    bot_client = bot_object.get_client_object()
    apollo_summarize_agent = deity.get_apollo_object()

    message_history = user_client.get_chat_history("athena_tgbot", limit=1)
    user_start_message = None

    async for message_entity in message_history:
        if message_entity.from_user.id == telegram_id:
            user_start_message = message_entity
            break

    try:
        # Extract and validate user ID
        requested_user_id = int(message.command[1].split("_")[1])
        user_id = message.from_user.id

        if user_id != requested_user_id:
            raise PermissionError("User ID mismatch")

        initial_message = message

        await user_start_message.edit_text(
            "can you give me the summary of the community I called you from?",
            parse_mode=enums.ParseMode.HTML,
        )

        waiting_message = await community_start_response(bot_client, initial_message)

        await asyncio.sleep(deity.get_telegram_draft_waiting_time())

        fetch_draft_peer_id = await wait_until_fresh_mention_found(
            user_client=user_client,
            username="@athena_tgbot",
            within_minutes=deity.get_telegram_draft_freshness_window(),
        )

        resolved_peer_info = await resolve_peer_id_for_summary(
            user_client=user_client,
            peer_id=fetch_draft_peer_id,
        )
        chat_hyperlink = resolved_peer_info.get_hyperlink()
        chat_entity_name = resolved_peer_info.get_entity_name()

        messages_clusters = await fetch_messages_from_last_x_hours(
            user_client=user_client,
            peer_id=fetch_draft_peer_id,
            hours=deity.get_telegram_message_batch_summary_hours(),
        )
        number_of_messages = len(messages_clusters)

        # Respond if the chat is empty
        if number_of_messages == 0:
            await waiting_message.reply_text(
                f"No messages found in <b>{chat_hyperlink}</b>",
                parse_mode=enums.ParseMode.HTML,
            )
            return

        # Respond with the number of messages found
        found_message = await community_found_response(
            bot_client, waiting_message, username, number_of_messages, chat_entity_name
        )

        summarize_messages = await apollo_summarize_agent.summarize_community_clusters(
            messages_clusters
        )
        follow_up_questions = await apollo_summarize_agent.generate_follow_up_questions(
            summarize_messages
        )

        detailed_summary = await create_detailed_community_summary_response(
            summarize_messages, resolved_peer_info
        )

        # Respond with the detailed summary
        summary_response = await community_summary(
            detailed_summary,
            username,
            found_message,
            resolved_peer_info,
            follow_up_questions,
        )

        return summary_response
    except (ValueError, IndexError) as e:
        logger.error(f"Error processing summary command: {e}")
        await message.reply("⚠️ Invalid request format")
    except PermissionError as e:
        await message.reply("🔒 Unauthorized access attempt logged")
        logger.warning(
            f"Security alert: User {message.from_user.id} tried accessing {requested_user_id}'s summary request"
        )


async def create_detailed_community_summary_response(
    summary: SumResp, peer_info: ResolvedPeerInfo
) -> str:
    """
    Create a community summary response
    """
    spoilers = []
    deep_link = peer_info.get_deep_link()
    return_text = peer_info.get_button_text()
    return_link = peer_info.get_button_link()

    deep_link_exists = peer_info.deep_link_exists()
    global_idx = 1
    entity_name = peer_info.get_entity_name()
    number_of_topics = len(summary.topics)

    for topic in summary.topics:
        message_links_array = []

        if deep_link_exists:
            # Easier to navigate the refs if message_ids are sorted
            message_ids = [int(message_id) for message_id in topic.message_ids]
            message_ids.sort()

            for message_id in message_ids:
                incremented_key = f"msg {global_idx}"
                hyperlink = f"<a href='{deep_link}/{message_id}'>{incremented_key}</a>"
                message_links_array.append(hyperlink)
                global_idx += 1

        if len(message_links_array) > 0:
            message_links_string = f"<i>({', '.join(message_links_array)})</i>"
        else:
            message_links_string = ""

        spoiler_text = (
            f"• <b>{topic.topic_name}</b>: {topic.summary} {message_links_string}"
        )
        spoilers.append(spoiler_text)

    header = f"<a href='{return_link}'>{entity_name}</a>:\n"
    summary_text = f"<blockquote expandable><i>Tap here to expand/collapse</i>\n{'\n'.join(spoilers)}</blockquote>\n"
    message = header + summary_text

    return message
