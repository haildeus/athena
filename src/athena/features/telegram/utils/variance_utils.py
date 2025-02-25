import asyncio
import random
from typing import Optional

from pyrogram import Client, enums
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

from src.athena.features.telegram.functions.chat_functions import send_typing_action
from src.athena.features.telegram.functions.sticker_functions import get_random_sticker
from src.athena.features.telegram.schemas.stickers_schemas import StickerUseCase
from src.athena.features.telegram.schemas.telegram_schemas import (
    FollowUpResp,
    MessageEffects,
    ResolvedPeerInfo,
)
from src.athena.features.telegram.utils.message_utils import streaming_message_helper


async def create_inline_keyboard_markup(
    follow_up_questions: FollowUpResp,
) -> InlineKeyboardMarkup:
    buttons = []
    for entry in follow_up_questions.questions:
        row = []
        row.append(
            InlineKeyboardButton(
                entry.question, callback_data=f"dig_deeper_{entry.index}"
            )
        )
        buttons.append(row)

    markup = InlineKeyboardMarkup(buttons)

    return markup


async def community_start_response(bot_client: Client, message: Message) -> Message:
    async def delayed_delete(message: Message, delay: int = 30):
        await asyncio.sleep(delay)
        await message.delete()

    chat_id = message.chat.id
    sticker_use_case = StickerUseCase.WAITING
    from_user = message.from_user
    username = from_user.first_name
    username = username.split(" ")[0]
    username = username.lower()

    text_options = [
        f"alright, {username}, im on it. lets see what kinda mess we're dealing with.",
        "copy. pulling the data stream now...",
        f"k, {username}, lemme grab my virtual coffee",
        f"got it, {username}. cutting out the noise.",
        "scanning...  let's hope there's something worthwhile in there.",
        f"i hear you, {username}.  just a sec...",
        f"again, {username}? you know you can just read the chat, right?",
        "another day another summary request. on it!",
    ]
    choice = random.choice(text_options)
    response = await message.reply_text(
        choice, parse_mode=enums.ParseMode.HTML, quote=True
    )

    send_sticker = random.choice([True, False])
    if send_sticker:
        sticker = await get_random_sticker(
            bot_client=bot_client,
            chat_id=chat_id,
            use_case=sticker_use_case,
        )
        file_id = sticker.file_id
        response = await message.reply_sticker(file_id)
        asyncio.create_task(delayed_delete(response, 15))

    await send_typing_action(bot_client, chat_id)
    return response


async def community_found_response(
    bot_client: Client,
    message: Message,
    username: str,
    number_of_messages: int,
    chat_entity_name: str,
) -> Message:
    chat_id = message.chat.id
    chat_entity_name = chat_entity_name.lower()
    username = username.lower()

    options = [
        f"found {number_of_messages} messages in {chat_entity_name}.  it's a mess...",
        f"{number_of_messages} messages?  you really let it pile up, huh?",
        f"okay, i've got {number_of_messages} messages from {chat_entity_name}.  brace yourself.",
        f"{number_of_messages} messages in {chat_entity_name}.  this is going to be... interesting.",
        f"wow, {number_of_messages} messages.  you've been busy (or not busy enough, apparently).",
    ]
    if number_of_messages > 500:
        options.append(
            f"are you kidding me, {username}? {number_of_messages} messages in {chat_entity_name}? i need a raise."
        )
    elif number_of_messages < 50:
        options.append(
            f"{username}, only {number_of_messages} msgs in {chat_entity_name}? you call that a community?"
        )

    choice = random.choice(options)
    response = await message.reply_text(
        choice,
        parse_mode=enums.ParseMode.HTML,
    )
    await send_typing_action(bot_client, chat_id)
    return response


async def post_community_summary_message(
    message: Message,
    follow_time: int = 20,
) -> Optional[Message]:
    no_follow_up = random.choices([True, False], weights=[0.4, 0.6], k=1)[0]
    if no_follow_up:
        return None

    await asyncio.sleep(follow_time)

    options_follow_up = [
        "let me know if you want to dig deeper",
        "anyway lmk if you want to know more",
        "i'm cool with exploring it further haha",
        "more info is a button away <s>(you know how to do it, right?)</s>",
    ]

    follow_up_message = await message.reply_text(
        random.choice(options_follow_up), parse_mode=enums.ParseMode.HTML
    )

    return follow_up_message


async def community_summary(
    summary: str,
    username: str,
    message: Message,
    resolved_peer_info: ResolvedPeerInfo,
    follow_up_questions: FollowUpResp,
) -> str:
    chat_entity_name = resolved_peer_info.get_entity_name().lower()
    username = username.lower()

    options_greetings = [
        f"that's TL;DR for {chat_entity_name}. <s>(you're welcome.)</s>",
        "that's basically what you missed!",
        "ok i turned that pile into a... slight smaller pile.",
        "happy to help.  hope it saves you some time.",
        f"yup, no need to thank me. you know you can count on me {username}.",
    ]

    choose_effect = random.choices([True, False], weights=[0.1, 0.9], k=1)[0]
    effect = (
        await choose_random_message_effect(positive=True) if choose_effect else None
    )

    summary_response = f"{summary}{random.choice(options_greetings)}"
    inline_keyboard_markup = await create_inline_keyboard_markup(follow_up_questions)

    response = await streaming_message_helper(
        message,
        summary_response,
        enums.ParseMode.HTML,
        quote=True,
        disable_web_page_preview=True,
        reply_markup=inline_keyboard_markup,
    )

    asyncio.create_task(post_community_summary_message(response))

    return response


async def choose_random_message_effect(positive: bool = True) -> int:
    if positive:
        return random.choice(
            [
                MessageEffects.FIRE.value,
                MessageEffects.THUMBS_UP.value,
                MessageEffects.HEART.value,
                MessageEffects.PARTY.value,
            ]
        )
    else:
        return random.choice(
            [
                MessageEffects.NEGATIVE.value,
                MessageEffects.POOP.value,
            ]
        )
