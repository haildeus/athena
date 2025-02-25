from typing import List, Optional
from pydantic import BaseModel, Field, model_serializer

from src.athena.core.utils import SafeFormatter


class TextContent(BaseModel):
    text: str


class MessageExample(BaseModel):
    user: str = Field(..., description="User name")
    content: TextContent = Field(..., description="Message content")
    action: Optional[str] = Field(
        None, description="Optional. Action to take on the message"
    )

    @model_serializer(mode="plain")
    def ser_message_example(self) -> str:
        return f"User: {self.user}\nContent: {self.content.text}" + (
            f"\nAction: {self.action}" if self.action else ""
        )


class StyleRules(BaseModel):
    general_style: List[str] = Field(
        ..., description="General style of the agent", min_length=1
    )
    conversation_style: List[str] = Field(
        ..., description="Conversation style of the agent", min_length=1
    )
    publication_style: List[str] = Field(
        ..., description="Publication style of the agent", min_length=1
    )

    @model_serializer(mode="plain")
    def ser_style_rules(self) -> dict:
        return {
            k: "\n".join(v) if isinstance(v, list) else v
            for k, v in self.__dict__.items()
        }


class Persona(BaseModel):
    """
    Persona represents the agent's or user's personality.
    """

    name: str = Field(description="Agent name", default="Athena")

    description: List[str] = Field(
        ...,
        description="Short snippets composed in random order to widen the possible outcomes",
        min_length=1,
    )
    backstory: List[str] = Field(
        ..., description="Factual, extracted from messages/tweets/past engagement"
    )

    adjectives: List[str] = Field(
        ..., description="Adjectives that describe the agent's personality"
    )
    topics: List[str] = Field(..., description="Topics that the agent can talk about")

    conversation_examples: List[List[MessageExample]] = Field(
        ..., description="Examples of messages that the agent can handle"
    )

    publications_examples: Optional[List[str]] = Field(
        None, description="Examples of posts/tweets that the agent would post"
    )

    style_rules: StyleRules = Field(..., description="Rules for the agent's style")

    # serialize for text
    @model_serializer(mode="plain")
    def ser_persona(self) -> dict:
        return {
            "name": self.name,
            "description": "\n".join(self.description),
            "backstory": "\n".join(self.backstory),
            "adjectives": ", ".join(self.adjectives),
            "topics": ", ".join(self.topics),
            "conversation_examples": "\n\n".join(
                "\n".join(str(e) for e in examples)
                for examples in self.conversation_examples
            ),
            "publications_examples": (
                "\n".join(self.publications_examples)
                if self.publications_examples
                else None
            ),
            "general_conversation": "\n".join(self.style_rules.general_style),
            "conversation_style": "\n".join(self.style_rules.conversation_style),
            "publication_style": "\n".join(self.style_rules.publication_style),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Persona":
        return cls(**data)

    """
    HELPER METHODS
    """

    def use_persona(self, string_to_format: str) -> str:
        formatter = SafeFormatter()
        persona_data = self.ser_persona()
        return formatter.format(string_to_format, **persona_data)

    def get_name(self) -> str:
        return self.name

    def get_description(self) -> List[str]:
        return self.description

    def get_backstory(self) -> List[str]:
        return self.backstory

    def get_adjectives(self) -> List[str]:
        return self.adjectives

    def get_topics(self) -> List[str]:
        return self.topics

    def get_conversation_examples(self) -> List[List[MessageExample]]:
        return self.conversation_examples

    def get_publications_examples(self) -> Optional[List[str]]:
        return self.publications_examples

    def get_general_conversation(self) -> List[str]:
        return self.style_rules.general_style

    def get_conversation_style(self) -> List[str]:
        return self.style_rules.conversation_style

    def get_publication_style(self) -> List[str]:
        return self.style_rules.publication_style
