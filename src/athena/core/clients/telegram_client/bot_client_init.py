import asyncio
from contextlib import asynccontextmanager

from pyrogram import Client, enums
from pyrogram.types import User

from src.athena.core import logger
from src.athena.core.clients.client_base import ClientBase
from src.athena.core.clients.telegram_client.telegram_config import (
    BotClientData,
    load_common_args,
    load_config,
)
from src.athena.features.telegram.handlers.bot_handlers import register_bot_handlers


class TelegramBotClient(ClientBase):
    """
    Initialize and manage Telegram MTProto bot client

    This client is used as the main entry point for the users
    """

    def __init__(self, deus=None):
        config = load_config()
        common_args = load_common_args()

        self.data = BotClientData()
        self.deus_instance = deus
        if not config.BOT_TOKEN:
            logger.error("BOT_TOKEN is not set in the config")
            raise ValueError("BOT_TOKEN is not set in the config")

        if not config.IN_MEMORY_SESSION:
            config.SESSION_DIR.mkdir(exist_ok=True, parents=True)

        self.client = Client(
            name=f"{config.SESSION_NAME}_bot",
            bot_token=config.BOT_TOKEN,
            **common_args,
        )
        self.client.action_scheduler = self.action_scheduler
        self.client.deus_instance = deus

    def __str__(self):
        return f"TelegramBotClient(bot_id={self.data.bot_id})"

    def get_client_object(self):
        return self.client

    def get_username(self) -> str:
        return self.data.bot_username

    async def start(self):
        try:
            logger.info("Starting Telegram bot client")
            await self.client.start()
            logger.info("Telegram bot client started")
            self._store_data(await self.client.get_me())
            logger.info(f"Bot client initialized for {self.data.bot_username}")
        except Exception as e:
            logger.error(f"Failed to start Telegram bot client: {e}")
            raise

        try:
            register_bot_handlers(self.client)
        except Exception as e:
            logger.error(f"Failed to register bot handlers: {e}")
            raise

    async def stop(self):
        """Stop the client and clean up dispatchers"""
        logger.info("Stopping Telegram bot client")
        stop_tasks = []

        # Stop dispatcher first
        logger.info("Stopping bot client dispatcher")
        self.client.dispatcher.updater_running = False
        for task in self.client.dispatcher.handler_worker_tasks:
            task.cancel()
        stop_tasks.append(self.client.stop())
        await asyncio.gather(*stop_tasks, return_exceptions=True)

    def _store_data(self, bot: User):
        self.data.bot_id = bot.id
        self.data.bot_username = bot.username

    @asynccontextmanager
    async def action_scheduler(
        self, chat_id: int, action: enums.ChatAction, delay: int = 5
    ):
        """Keep sending chat action until context exits"""
        stop_event = asyncio.Event()

        async def action_loop():
            while not stop_event.is_set():
                await self.client.send_chat_action(chat_id, action)
                await asyncio.sleep(delay)

        task = asyncio.create_task(action_loop())
        try:
            yield
        finally:
            stop_event.set()
            await task
