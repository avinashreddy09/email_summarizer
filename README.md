# Bulk Email Summarizer (Lazy Automation – Week 2, AI for Bharat)

> "I hate wading through a messy inbox, so I built an AI to summarize it."

This project is my submission for **AI for Bharat – Week 2: Lazy Automation**.  
It connects to my email inbox, fetches unread emails from a recent time window, and uses **Amazon Bedrock (Claude 3)** to generate a concise summary with action items.

---

## ✨ Features

- Fetches **unread** emails via IMAP (Gmail by default).
- Looks back over the **last N hours** (configurable, default 24).
- Normalizes emails into a simple structure: subject, sender, date, snippet.
- Sends the context to **Anthropic Claude 3 on Amazon Bedrock** for summarization.
- Saves the result as a **Markdown report** in `reports/`.
- Includes a `.kiro` directory to demonstrate **Kiro spec-driven development**.

---

## 🧱 Tech Stack

- Python 3.10+
- `imaplib`, `email` (standard library)
- `boto3` for Amazon Bedrock Runtime
- `python-dotenv` for environment-based config
- Kiro for specs & automated workflows (`/.kiro`)

---

## 📂 Project Structure

```text
email-summarizer/
  .kiro/
    config.json
    specs/
      email_summarizer.yaml
  src/
    main.py
    email_fetcher.py
    summarizer.py
    config.py
  reports/
  requirements.txt
  .env.example
  .gitignore
  README.md
