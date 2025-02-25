import asyncio
from typing import Union

from pydantic_ai import Agent

from src.athena.core import logger
from src.athena.core.clients import TelegramAccountClient, TelegramBotClient
from src.athena.features.telegram.ai_services.agents import ApolloSummarizeAgent

from ...ai_models import LLMBase
from ...organon import OrganonModel
from ..schemas import Persona, Powers, Settings, SupportedClients
from .base_abstract import DeusAbstract
from .base_persona import BASE_ESSENCE

BASE_PERSONA = BASE_ESSENCE.persona
BASE_POWERS = BASE_ESSENCE.powers
BASE_SETTINGS = BASE_ESSENCE.settings


class Deus(DeusAbstract):
    """
    Abstract base class for all Deus implementations
    """

    def __init__(self):
        self.persona = BASE_PERSONA
        self.powers = BASE_POWERS
        self.settings = BASE_SETTINGS

        self.clients = {}
        self.model = self.powers.selected_model.value()
        self.agent = self.model.agent

        self.apollo_summarize_agent = ApolloSummarizeAgent(
            self.get_model(), self.get_persona(), self
        )
        self.telegram_user = TelegramAccountClient(self)
        self.telegram_bot = TelegramBotClient(self)

        self.organon = OrganonModel(self.get_model())

    async def start(self):
        """
        Start the Deus client
        """
        try:
            async_clients = []
            for client in self.powers.selected_clients:
                client_object = self._resolve_client_to_instance(client)
                self.clients[client.name] = client_object
                async_clients.append(client_object.start())

            await asyncio.gather(*async_clients)  # Waits for all the clients to launch
        except Exception as e:
            logger.error(f"Error starting clients: {e}")
            raise e

    def get_apollo_object(self) -> ApolloSummarizeAgent:
        """
        Get the Apollo object
        """
        return self.apollo_summarize_agent

    def _resolve_client_to_instance(self, client_name: SupportedClients):
        """
        Resolve a client name to an instance
        """
        response_dict = {
            SupportedClients.TELEGRAM_USER: self.telegram_user,
            SupportedClients.TELEGRAM_BOT: self.telegram_bot,
        }
        try:
            return response_dict[client_name]
        except KeyError:
            raise ValueError(f"Client {client_name} not found")

    def format_template(self, string_to_format: str) -> str:
        """
        Use the persona to format a string
        """
        try:
            return self.persona.use_persona(string_to_format)
        except Exception as e:
            self.logger.error(f"Error formatting template: {e}")
            raise e

    def get_agent(self) -> Agent:
        """
        Get the agent of the Pantheon
        """
        return self.agent

    def get_model(self) -> LLMBase:
        """
        Get the model of the Pantheon
        """
        return self.model

    def get_name(self) -> str:
        """
        Get the name of the Pantheon
        """
        return self.persona.name

    def get_persona(self) -> Persona:
        """
        Get the persona of the Pantheon
        """
        return self.persona

    def get_client(
        self, client_name: str
    ) -> Union[TelegramAccountClient, TelegramBotClient]:
        """
        Get the client of the Deus instance
        """
        try:
            return self.clients[client_name]
        except KeyError:
            raise ValueError(f"Client {client_name} not found")

    def get_telegram_draft_waiting_time(self) -> int:
        """
        Get the draft waiting time
        """
        return self.settings.telegram_settings.BOT_DRAFT_WAITING_TIME

    def get_telegram_draft_freshness_window(self) -> int:
        """
        Get the draft freshness window
        """
        return self.settings.telegram_settings.BOT_DRAFT_FRESHNESS_WINDOW

    def get_telegram_message_batch_summary(self) -> int:
        """
        Get the message batch summary
        """
        return self.settings.telegram_settings.MESSAGE_BATCH_SUMMARY_SIZE

    def get_telegram_message_batch_summary_hours(self) -> int:
        """
        Get the message batch summary hours
        """
        return self.settings.telegram_settings.MESSAGE_BATCH_SUMMARY_HOURS

    def get_telegram_welcome_message(self) -> str:
        """
        Get the welcome message
        """
        return self.settings.telegram_settings.BOT_WELCOME_MESSAGE

    def get_organon(self):
        return self.organon


class DeusMaker(Deus):
    """
    Maker class for creating Deus instances
    """

    def __init__(self, persona: Persona, powers: Powers, settings: Settings):
        super().__init__()
        self.persona = persona
        self.powers = powers
        self.settings = settings

    def __str__(self) -> str:
        return f"Deus(persona={self.persona}, powers={self.powers}, settings={self.settings})"
