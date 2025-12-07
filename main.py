# src/main.py
import argparse
import datetime as dt
from pathlib import Path

from .config import load_config
from .email_fetcher import fetch_unread_since
from .summarizer import summarize_emails


def _build_report_markdown(summary: str, count: int, hours: int) -> str:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""# Email Summary Report

Generated at: **{now}**
Time window: **last {hours} hours**
Unread emails considered: **{count}**

---

## AI Summary

{summary}
"""


def main():
    parser = argparse.ArgumentParser(
        description="Summarize unread emails using Amazon Bedrock (Claude)."
    )
    parser.add_argument(
        "--hours",
        type=int,
        help="Look back this many hours for unread emails (default from env or 24).",
    )
    args = parser.parse_args()

    cfg = load_config()
    since_hours = args.hours or cfg.summary_since_hours

    print(f"🔍 Fetching unread emails from last {since_hours} hours...")

    emails = fetch_unread_since(cfg.email, since_hours=since_hours)
    print(f"📨 Found {len(emails)} unread email(s).")

    summary = summarize_emails(cfg.bedrock, emails)

    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M")
    report_path = reports_dir / f"email_summary_{timestamp}.md"

    report_md = _build_report_markdown(
        summary=summary,
        count=len(emails),
        hours=since_hours,
    )

    report_path.write_text(report_md, encoding="utf-8")

    print(f"✅ Summary generated: {report_path}")
    print("\n---\n")
    print(summary)


if __name__ == "__main__":
    main()
