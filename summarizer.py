# src/summarizer.py
import json
from typing import List

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from .config import BedrockConfig
from .email_fetcher import SimpleEmail


def _build_prompt(emails: List[SimpleEmail]) -> str:
    if not emails:
        return "There are no unread emails."

    lines = [
        "You are an assistant that summarizes unread emails for a busy developer.",
        "",
        "Summarize the following emails into:",
        "1) A short overview (3–5 bullet points).",
        "2) A list of concrete action items with owners and due dates if mentioned.",
        "3) A quick priority ranking: HIGH / MEDIUM / LOW buckets.",
        "",
        "Emails:",
    ]

    for idx, em in enumerate(emails, start=1):
        lines.append(f"\nEmail #{idx}")
        lines.append(f"From: {em.sender}")
        lines.append(f"Date: {em.date}")
        lines.append(f"Subject: {em.subject}")
        lines.append(f"Snippet: {em.snippet}")

    return "\n".join(lines)


def summarize_emails(
    cfg: BedrockConfig,
    emails: List[SimpleEmail],
) -> str:
    if not emails:
        return "No unread emails found in the selected time window."

    prompt = _build_prompt(emails)

    client = boto3.client("bedrock-runtime", region_name=cfg.region)

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    }
                ],
            }
        ],
    }

    try:
        response = client.invoke_model(
            modelId=cfg.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )
        resp_body = json.loads(response["body"].read())
        # Claude on Bedrock returns: { ..., "content": [{"type":"text","text":"..."}], ... }
        content = resp_body.get("content", [])
        if content and isinstance(content, list):
            return content[0].get("text", "").strip() or "No summary generated."
        return "Model returned no content."
    except (BotoCoreError, ClientError, KeyError, ValueError) as e:
        # Fallback: degrade gracefully
        fallback_lines = [
            "⚠️ Bedrock call failed, falling back to a simple subject-only summary.",
            f"Error: {e}",
            "",
            "Unread emails:",
        ]
        for em in emails:
            fallback_lines.append(f"- {em.subject} — {em.sender}")
        return "\n".join(fallback_lines)
