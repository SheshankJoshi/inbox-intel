# InboxIntel

InboxIntel is an autonomous multi-agent pipeline that reads incoming emails, sends email content to an OpenAI-compatible LLM endpoint for classification and link extraction, fetches metadata, and publishes a daily digest as JSON, Markdown, and HTML.

## What Is Implemented

- Supervisor orchestration agent with end-to-end workflow state.
- Email ingestion via:
  - sample JSON emails (default, no credentials)
  - IMAP inbox (Gmail/Outlook compatible with app passwords)
- LLM-driven email classifier agent (no keyword heuristics).
- LLM-driven link extraction agent (no regex/keyword URL heuristics).
- Article metadata fetch agent (title, description, publisher, publication date, summary).
- Digest builder agent producing structured output.
- Publisher agent that writes:
  - `output/digest.json`
  - `output/digest.md`
  - `output/digest.html`
- Optional FastAPI server:
  - `GET /health`
  - `GET /api/digest`
  - `GET /` (HTML digest page)

## Project Structure

```text
inbox-intel/
|-- agents/
|   |-- supervisor.py
|   |-- email_ingestion.py
|   |-- classifier.py
|   |-- link_extractor.py
|   |-- metadata_agent.py
|   |-- digest_builder.py
|   `-- publisher.py
|-- tools/
|   |-- email_reader_mcp.py
|   |-- http_fetch_mcp.py
|   |-- openai_custom_client.py
|   `-- html_parser.py
|-- config/
|   |-- agent_manifest.json
|   `-- mcp_server.yaml
|-- demo/
|   |-- sample_emails/
|   `-- demo_script.md
|-- output/
|-- prompts/
|   `-- llm_prompts.yaml
|-- schemas/
|   `-- llm_outputs.py
|-- models.py
|-- run.py
|-- main.py
`-- .env.example
```

## Quick Start

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure custom LLM endpoint and key

```bash
cp .env.example .env
```

Set these required values in `.env`:

- `INBOX_INTEL_OPENAI_BASE_URL`
- `INBOX_INTEL_OPENAI_API_KEY`
- `INBOX_INTEL_OPENAI_MODEL`

Optional compatibility settings for non-standard servers:

- `INBOX_INTEL_OPENAI_CHAT_PATH` (default: `/v1/chat/completions`)
- `INBOX_INTEL_OPENAI_KEY_HEADER` (default: `Authorization`)
- `INBOX_INTEL_OPENAI_KEY_PREFIX` (default: `Bearer`)
- `INBOX_INTEL_OPENAI_TIMEOUT_SECONDS` (default: `45`)
- `INBOX_INTEL_PROMPTS_FILE` (default: `prompts/llm_prompts.yaml`)

### 4. Run in sample mode (default)

```bash
python run.py
```

This uses emails under `demo/sample_emails/` and writes digest artifacts to `output/`.

### 5. Open generated outputs

- HTML report: `output/digest.html`
- JSON API payload: `output/digest.json`
- Markdown report: `output/digest.md`

## Run With API Server

```bash
python run.py --serve --host 127.0.0.1 --port 8000
```

Then open:

- `http://127.0.0.1:8000/` for HTML digest
- `http://127.0.0.1:8000/api/digest` for JSON

## IMAP Mode (Real Inbox)

### 1. Ensure `.env` contains both IMAP and LLM settings

Set:

- `INBOX_INTEL_SOURCE=imap`
- `INBOX_INTEL_IMAP_HOST` (example: `imap.gmail.com`)
- `INBOX_INTEL_IMAP_PORT` (usually `993`)
- `INBOX_INTEL_IMAP_MAILBOX` (usually `INBOX`)
- `INBOX_INTEL_EMAIL_USERNAME`
- `INBOX_INTEL_EMAIL_PASSWORD` (use app password where required)

### 2. Run

```bash
python run.py --source imap --max-emails 25
```

You can combine with server mode:

```bash
python run.py --source imap --serve
```

## Command Reference

```bash
python run.py \
  --source sample|imap \
  --max-emails 25 \
  --output-dir output \
  --serve \
  --host 127.0.0.1 \
  --port 8000
```

## Architecture Summary

1. `EmailIngestionAgent` fetches unread emails.
2. `EmailClassifierAgent` uses your custom OpenAI-compatible endpoint to classify each email.
3. If category is Newsfeed, `LinkExtractionAgent` uses the same endpoint to extract article URLs.
4. `ArticleMetadataAgent` fetches metadata for each URL.
5. `DigestBuilderAgent` creates structured daily digest.
6. `PublisherAgent` writes JSON/Markdown/HTML and optionally serves API/UI.
7. `SupervisorAgent` coordinates everything and tracks run metrics.

## Notes

- Classification and link extraction are fully LLM-driven.
- LLM prompt templates are stored in `prompts/llm_prompts.yaml`.
- LLM output contracts are defined with Pydantic models in `schemas/llm_outputs.py`.
- Metadata extraction uses Open Graph/meta tags where available.
- Duplicate URLs are removed before digest publication.
