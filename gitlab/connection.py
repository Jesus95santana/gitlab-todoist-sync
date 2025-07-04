# gitlab/connection.py

import os
from dotenv import load_dotenv

load_dotenv()


def get_gitlab_url():
    url = os.getenv("GITLAB_URL")
    if not url:
        raise Exception("GITLAB_URL not set in .env or environment variables.")
    return url


def get_gitlab_pat_token():
    token = os.getenv("PRIVATE_TOKEN")
    if not token:
        raise Exception("PRIVATE_TOKEN not set in .env or environment variables.")
    return token


def get_gitlab_headers():
    return {"PRIVATE-TOKEN": get_gitlab_pat_token()}
