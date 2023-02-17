from pydantic import BaseModel


class OpenAISchema(BaseModel):
    question: str
