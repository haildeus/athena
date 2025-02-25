from abc import ABC, abstractmethod


class ClientBase(ABC):
    @abstractmethod
    async def start(self):
        """Start the client"""
        pass

    @abstractmethod
    async def stop(self):
        """Stop the client"""
        pass

    @abstractmethod
    def get_username(self) -> str:
        """Get the username of the client"""
        pass

    @abstractmethod
    def get_client_object(self):
        """Get the client object"""
        pass
