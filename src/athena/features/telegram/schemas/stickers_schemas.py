import random
from typing import List, Optional
from enum import Enum


from pydantic import BaseModel, Field, model_validator


class StickerFamiliarityLevel(Enum):
    """
    Enum representing the familiarity level of a sticker
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class StickerUseCase(Enum):
    """
    Enum representing the use case of a sticker
    """

    WAITING = "waiting"
    GREETING = "greeting"
    FAREWELL = "farewell"
    ERROR = "error"
    POSITIVE = "positive"
    NEGATIVE = "negative"
    MEMETIC = "memetic"


class StickerGender(Enum):
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class StickerFetchResponse(BaseModel):
    """
    Schema modelling the response from the sticker fetch
    """

    sticker: str = Field(..., description="The sticker to send")
    set_name: str = Field(..., description="The name of the sticker set")
    familiarity_level: StickerFamiliarityLevel = Field(
        ..., description="The familiarity level of the sticker set"
    )
    gender: StickerGender = Field(..., description="The gender of the sticker set")


class Stickers(BaseModel):
    """
    Stickers are split based on use cases:
    - Waiting: Before func execution
    - Greeting: Greeting the user
    - Farewell: As a goodbye
    - Error: When an error occurs
    - Positive: Positive response
    - Negative: Negative response
    - Memetic: Memetic response
    """

    waiting: Optional[List[str]] = Field(
        [], description="Stickers to send when the bot is waiting for a response"
    )
    greeting: Optional[List[str]] = Field(
        [], description="Stickers to send when the bot greets the user"
    )
    farewell: Optional[List[str]] = Field(
        [], description="Stickers to send when the bot says goodbye"
    )
    error: Optional[List[str]] = Field(
        [], description="Stickers to send when an error occurs"
    )
    positive: Optional[List[str]] = Field(
        [], description="Stickers to send when the bot has a positive response"
    )
    negative: Optional[List[str]] = Field(
        [], description="Stickers to send when the bot has a negative response"
    )
    memetic: Optional[List[str]] = Field(
        [], description="Stickers to send when the bot has a memetic response"
    )

    @model_validator(mode="before")
    def validate_stickers(cls, data):
        """
        Validate that at least one sticker is present
        """
        if (
            not data.get("waiting")
            and not data.get("greeting")
            and not data.get("farewell")
            and not data.get("error")
            and not data.get("positive")
            and not data.get("negative")
            and not data.get("memetic")
        ):
            raise ValueError("At least one sticker must be provided")
        return data


class StickerSet(BaseModel):
    """
    Schema representing a Telegram sticker set.
    """

    set_name: str = Field(..., description="Required to fetch the sticker information")

    familiarity_level: Optional[StickerFamiliarityLevel] = Field(
        StickerFamiliarityLevel.MEDIUM,
        description="The familiarity level of the sticker set",
    )
    gender: Optional[StickerGender] = Field(
        StickerGender.NEUTRAL, description="The gender of the sticker set"
    )

    stickers: Stickers = Field(..., description="Stickers to send")

    def get_sticker(self, use_case: StickerUseCase) -> Optional[StickerFetchResponse]:
        """
        Get a random sticker from the list of stickers
        """
        if use_case_stickers := getattr(self.stickers, use_case.value):
            response = random.choice(use_case_stickers)
            return StickerFetchResponse(
                sticker=response,
                set_name=self.set_name,
                familiarity_level=self.familiarity_level,
                gender=self.gender,
            )
        return None


class SupportedStickerSets(BaseModel):
    """
    Schema representing the supported sticker sets
    """

    sticker_sets: List[StickerSet] = Field(
        ..., description="The available sticker sets"
    )

    def get_sticker_set(self, set_name: str) -> StickerSet:
        """
        Gets a particular sticker set by name
        """
        for sticker_set in self.sticker_sets:
            if sticker_set.set_name == set_name:
                return sticker_set
        raise ValueError(f"Sticker set {set_name} not found")

    def get_random_set(
        self, familiarity_level: Optional[StickerFamiliarityLevel] = None
    ) -> StickerSet:
        """
        Selects a random set within the given familiarity level

        If no familiarity level is provided, selects a random set
        """
        selection = (
            [
                sticker_set
                for sticker_set in self.sticker_sets
                if sticker_set.familiarity_level == familiarity_level
            ]
            if familiarity_level
            else self.sticker_sets
        )
        return random.choice(selection)

    def get_random_sticker(
        self,
        use_case: StickerUseCase,
        familiarity_level: Optional[StickerFamiliarityLevel] = None,
    ) -> Optional[StickerFetchResponse]:
        """
        Selects a random set within the given familiarity level
        Fetches a random sticker from the selected set

        Tries up to 3 times to get a sticker
        """
        for _ in range(3):
            sticker_set = self.get_random_set(familiarity_level)
            if response := sticker_set.get_sticker(use_case):
                return response
        return None


"""
SETTING UP AVAILABLE STICKERS
"""

regular_dude_stickers = Stickers(
    waiting=["🫠", "😞", "🤓"],
    greeting=["😃"],
    farewell=[],
    error=["😔"],
    positive=["😃"],
    negative=["😔", "😖"],
    memetic=["🤑", "🫠"],
)

milady_stickers = Stickers(
    waiting=["😶"],
    greeting=["❤️", "☀️"],
    farewell=["🐥"],
    error=["🤟"],
    positive=["❤️", "😈", "👍"],
    negative=["😡", "🧐", "🤔"],
    memetic=["🙏"],
)

judy_stickers = Stickers(
    waiting=["👍", "🤔"],
    greeting=["👋", "😴"],
    farewell=["😴"],
    error=["🤷‍♀️", "😢"],
    positive=["😂", "😘", "👍", "❤️"],
    negative=["🙅‍♀️", "😭"],
    memetic=["😴", "😔"],
)

REGULAR_DUDE_SET = StickerSet(
    set_name="Alliance_Mascot",
    familiarity_level=StickerFamiliarityLevel.MEDIUM,
    gender=StickerGender.NEUTRAL,
    stickers=regular_dude_stickers,
)

MILADY_SET = StickerSet(
    set_name="MiladyWO",
    familiarity_level=StickerFamiliarityLevel.HIGH,
    gender=StickerGender.NEUTRAL,
    stickers=milady_stickers,
)

JUDY_SET = StickerSet(
    set_name="JudyAlvarez",
    familiarity_level=StickerFamiliarityLevel.MEDIUM,
    gender=StickerGender.FEMALE,
    stickers=judy_stickers,
)

"""
SUPPORTING STICKER SETS
"""

SUPPORTED_STICKER_SETS = SupportedStickerSets(
    sticker_sets=[REGULAR_DUDE_SET, MILADY_SET, JUDY_SET],
)
