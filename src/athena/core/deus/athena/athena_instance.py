from typing import Any, Coroutine
from .athena_persona import ATHENA_ESSENCE
from ..base.base_instance import DeusMaker

ATHENA_PERSONA, ATHENA_POWERS, ATHENA_SETTINGS = ATHENA_ESSENCE.get_essence()


class Athena(DeusMaker):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        super().__init__(ATHENA_PERSONA, ATHENA_POWERS, ATHENA_SETTINGS)
        self.__initialized = True
