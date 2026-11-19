import os

from dotenv import load_dotenv
from openai import APIError, OpenAI
from pydantic import BaseModel

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ProjectExtraction(BaseModel):
    title: str
    summary: str
    technologies: list[str]


class ModelRefusalError(Exception):
    pass


class ProviderUnavailableError(Exception):
    pass


def extract_project(notes: str) -> ProjectExtraction:
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract a concise portfolio project from the user's notes. "
                        "Return a short title, a one or two sentence summary, and "
                        "the technologies mentioned or clearly implied."
                    ),
                },
                {"role": "user", "content": notes},
            ],
            response_format=ProjectExtraction,
            temperature=0.1,
        )
    except APIError as error:
        raise ProviderUnavailableError from error

    message = response.choices[0].message
    if message.refusal or message.parsed is None:
        raise ModelRefusalError
    return message.parsed
