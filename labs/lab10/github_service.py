import os

import requests
from dotenv import load_dotenv

load_dotenv()


class RepositoryNotFoundError(Exception):
    pass


class ReadmeTooShortError(Exception):
    pass


class GitHubUnavailableError(Exception):
    pass


def fetch_repository_readme(owner: str, repo: str) -> str:
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/readme",
            headers=headers,
            timeout=10,
        )
    except requests.RequestException as error:
        raise GitHubUnavailableError from error

    if response.status_code == 404:
        raise RepositoryNotFoundError
    if not response.ok:
        raise GitHubUnavailableError

    try:
        readme = response.json().get("content", "")
        import base64

        readme = base64.b64decode(readme).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        raise GitHubUnavailableError

    if len(readme.strip()) < 20:
        raise ReadmeTooShortError

    return readme[:4000]
