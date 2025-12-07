# src/email_fetcher.py
import datetime as dt
import email
import imaplib
from dataclasses import dataclass
from email.header import decode_header
from typing import List, Optional

from .config import EmailConfig


@dataclass
class SimpleEmail:
    subject: str
    sender: str
    date: str
    snippet: str


def _decode_header(value: Optional[str]) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    decoded = []
    for text, enc in parts:
        if isinstance(text, bytes):
            decoded.append(text.decode(enc or "utf-8", errors="ignore"))
        else:
            decoded.append(text)
    return " ".join(decoded)


def _get_text_part(msg: email.message.Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    return part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8",
                        errors="ignore",
                    )
                except Exception:
                    continue
    else:
        if msg.get_content_type() == "text/plain":
            try:
                return msg.get_payload(decode=True).decode(
                    msg.get_content_charset() or "utf-8",
                    errors="ignore",
                )
            except Exception:
                pass
    return ""


def _imap_date(d: dt.datetime) -> str:
    # IMAP wants: 07-Dec-2025
    return d.strftime("%d-%b-%Y")


def fetch_unread_since(
    cfg: EmailConfig,
    since_hours: int = 24,
) -> List[SimpleEmail]:
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=since_hours)

    if cfg.use_ssl:
        mailbox = imaplib.IMAP4_SSL(cfg.host, cfg.port)
    else:
        mailbox = imaplib.IMAP4(cfg.host, cfg.port)

    mailbox.login(cfg.username, cfg.password)
    mailbox.select(cfg.folder)

    since_str = _imap_date(cutoff)
    status, data = mailbox.search(None, "UNSEEN", f'(SINCE "{since_str}")')

    emails: List[SimpleEmail] = []

    if status != "OK":
        mailbox.logout()
        return emails

    ids = data[0].split()
    for msg_id in ids:
        status, msg_data = mailbox.fetch(msg_id, "(RFC822)")
        if status != "OK":
            continue

        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)

        subject = _decode_header(msg.get("Subject"))
        sender = _decode_header(msg.get("From"))
        date = _decode_header(msg.get("Date"))
        body = _get_text_part(msg)

        snippet = body.strip().replace("\r", " ").replace("\n", " ")
        if len(snippet) > 300:
            snippet = snippet[:297] + "..."

        emails.append(
            SimpleEmail(
                subject=subject or "(no subject)",
                sender=sender or "(unknown sender)",
                date=date or "",
                snippet=snippet or "(no preview available)",
            )
        )

    mailbox.close()
    mailbox.logout()
    return emails
