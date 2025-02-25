import asyncio

from pyrogram import Client
from pyrogram.types import User

from src.athena.core.clients.telegram_client.telegram_config import (
    load_config,
    load_common_args,
    ClientData,
)
from src.athena.core.clients.client_base import ClientBase
from src.athena.core.system import logger


class TelegramAccountClient(ClientBase):
    """Initialize and manage Telegram MTProto client"""

    def __init__(self, deus=None):
        config = load_config()
        common_args = load_common_args()
        self.client_data = ClientData()
        self.deus_instance = deus

        # Validate both credentials are present
        if not config.IN_MEMORY_SESSION:
            config.SESSION_DIR.mkdir(exist_ok=True, parents=True)
        if not config.PHONE_NUMBER:
            logger.error("PHONE_NUMBER is not set in the config")
            raise ValueError("PHONE_NUMBER must be provided for this configuration")

        self.client = Client(
            name=f"{config.SESSION_NAME}_user",
            **common_args,
        )
        self.client.deus_instance = deus

    def __str__(self):
        return f"TelegramAccountClient(user_id={self.client_data.user_id})"

    def get_client_object(self):
        return self.client

    def get_username(self) -> str:
        username = self.client_data.first_name or self.client_data.username
        return username

    def get_first_name_short(self) -> str:
        username = self.get_username()
        return username.split(" ")[0] if username else None

    def get_telegram_id(self) -> str:
        return self.client_data.user_id

    async def start(self):
        """Start clients with proper initialization order"""
        try:
            # Start user client first to establish session
            logger.info("User client initilization")
            await self.client.start()
            self._store_data(await self.client.get_me())
            logger.info(f"User client initialized for {self.client_data.username}")
            # Allow event loop to process
            await asyncio.sleep(0.5)

        except Exception as e:
            logger.error(f"Client startup failed: {str(e)}")
            await self.stop()
            raise RuntimeError(f"Client startup failed: {str(e)}") from e

    async def stop(self):
        """Stop the client and clean up dispatchers"""
        logger.info("Stopping Telegram client")
        stop_tasks = []

        # Stop dispatcher first
        logger.info("Stopping user client dispatcher")
        self.client.dispatcher.updater_running = False
        for task in self.client.dispatcher.handler_worker_tasks:
            task.cancel()
        stop_tasks.append(self.client.stop())
        await asyncio.gather(*stop_tasks, return_exceptions=True)

        # Clean up references
        logger.info("Cleaning up client references")
        self.client = None

    def _store_data(self, user: User):
        self.client_data.user_id = user.id
        self.client_data.is_premium = user.is_premium
        self.client_data.username = user.username
        self.client_data.first_name = user.first_name
