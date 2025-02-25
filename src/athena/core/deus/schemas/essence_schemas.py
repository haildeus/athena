from typing import Tuple
from pydantic import BaseModel

from . import Persona, Powers, Settings


class Essence(BaseModel):
    persona: Persona
    powers: Powers
    settings: Settings

    @classmethod
    def from_dict(cls, persona: dict, powers: dict, settings: dict) -> "Essence":
        return cls(
            persona=Persona.from_dict(persona),
            powers=Powers.from_dict(powers),
            settings=Settings.from_dict(settings),
        )

    def get_essence(self) -> Tuple[Persona, Powers, Settings]:
        return (self.persona, self.powers, self.settings)
