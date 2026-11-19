import os
import uuid
from typing import Literal

from dotenv import load_dotenv
from openai import APIError, OpenAI
from pydantic import BaseModel

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ProjectExtraction(BaseModel):
    title: str
    summary: str
    technologies: list[str]


class GitHubDraft(BaseModel):
    title: str
    summary: str
    technologies: list[str]
    difficulty: Literal["Beginner", "Intermediate", "Advanced"]


class ModelRefusalError(Exception):
    pass


class ProviderUnavailableError(Exception):
    pass


git_sessions = {}


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


def create_git_draft(readme: str) -> tuple[str, GitHubDraft]:
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Create a concise portfolio project draft from the repository "
                        "README. Return a short title, a summary of one or two sentences, "
                        "a list of technologies, and exactly one difficulty: Beginner, "
                        "Intermediate, or Advanced."
                    ),
                },
                {"role": "user", "content": readme[:4000]},
            ],
            response_format=GitHubDraft,
            temperature=0.1,
        )
    except APIError as error:
        raise ProviderUnavailableError from error

    message = response.choices[0].message
    if message.refusal or message.parsed is None:
        raise ModelRefusalError

    session_id = str(uuid.uuid4())
    git_sessions[session_id] = {
        "draft": message.parsed,
        "history": [
            {
                "role": "system",
                "content": "Refine a portfolio project draft based on README context and user feedback.",
            },
            {"role": "user", "content": readme[:4000]},
            {"role": "assistant", "content": message.parsed.model_dump_json()},
        ],
    }
    return session_id, message.parsed


def refine_git_draft(session_id: str, feedback: str) -> GitHubDraft:
    session = git_sessions.get(session_id)
    if session is None:
        return None

    session["history"].append({"role": "user", "content": feedback})
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=session["history"],
            response_format=GitHubDraft,
            temperature=0.1,
        )
    except APIError as error:
        raise ProviderUnavailableError from error

    message = response.choices[0].message
    if message.refusal or message.parsed is None:
        raise ModelRefusalError

    session["draft"] = message.parsed
    session["history"].append({"role": "assistant", "content": message.parsed.model_dump_json()})
    return message.parsed


def get_git_draft(session_id: str):
    session = git_sessions.get(session_id)
    if session is None:
        return None
    return session["draft"]
