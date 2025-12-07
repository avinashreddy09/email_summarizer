# src/config.py
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class EmailConfig:
    host: str
    port: int
    username: str
    password: str
    folder: str = "INBOX"
    use_ssl: bool = True


@dataclass
class BedrockConfig:
    region: str
    model_id: str


@dataclass
class AppConfig:
    email: EmailConfig
    bedrock: BedrockConfig
    summary_since_hours: int = 24


def load_config() -> AppConfig:
    email = EmailConfig(
        host=os.environ.get("EMAIL_HOST", "imap.gmail.com"),
        port=int(os.environ.get("EMAIL_PORT", "993")),
        username=os.environ["EMAIL_USER"],
        password=os.environ["EMAIL_PASSWORD"],
    )

    bedrock = BedrockConfig(
        region=os.environ.get("BEDROCK_REGION", "us-east-1"),
        model_id=os.environ.get(
            "BEDROCK_MODEL_ID",
            "anthropic.claude-3-haiku-20240307-v1:0",
        ),
    )

    since_hours = int(os.environ.get("SUMMARY_SINCE_HOURS", "24"))

    return AppConfig(email=email, bedrock=bedrock, summary_since_hours=since_hours)
