import os
from typing import List
from requests import Response, post


FAILED_DOMAIN = "Failed to load Mailgun domain."
FAILED_API_KEY = "Failed to load Mailgun API key."
FAILED_SEND_EMAIL = "Error sending activation email, user registration failed."


class MailgunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Mailgun:
    MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")
    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")

    FROM_TITLE = os.environ.get("APP_NAME")
    FROM_EMAIL = os.environ.get("FROM_EMAIL")

    @classmethod
    def send_email(cls, email: List[str], subject: str, text: str, html: str) -> Response:
        if cls.MAILGUN_DOMAIN is None:
            raise MailgunException(FAILED_DOMAIN)

        if cls.MAILGUN_API_KEY is None:
            raise MailgunException(FAILED_API_KEY)

        response = post(
            f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
            auth=("api", cls.MAILGUN_API_KEY),
            data={
                "from": f"{cls.FROM_TITLE} <{cls.FROM_EMAIL}>",
                "to": email,
                "subject": subject,
                "text": text,
                "html": html
            }
        )

        if response.status_code != 200:
            raise MailgunException(FAILED_SEND_EMAIL)

        return response
