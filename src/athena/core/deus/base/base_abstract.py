from abc import ABC, abstractmethod


class DeusAbstract(ABC):
    """
    Abstract base class for all Deus instances
    """

    @abstractmethod
    async def start(self):
        """
        Start the Deus instance
        """
        pass

    @abstractmethod
    async def format_template(self, string_to_format: str) -> str:
        """
        Format a string using the Deus instance
        """
        pass

    @abstractmethod
    async def get_agent(self):
        """
        Get the agent of the Deus instance
        """
        pass

    @abstractmethod
    async def get_model(self):
        """
        Get the model of the Deus instance
        """
        pass

    @abstractmethod
    async def get_client(self, client_name: str):
        """
        Get a client by name
        """
        pass

    @abstractmethod
    async def get_persona(self):
        """
        Get the persona of the Deus instance
        """
        pass

    @abstractmethod
    def get_organon(self):
        """
        Get the organon of the Deus instance
        """
        pass
