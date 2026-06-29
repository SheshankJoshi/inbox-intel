from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
import uvicorn

from models import DailyDigest


class PublisherAgent:
    def __init__(self, output_dir: str = "output") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def publish(self, digest: DailyDigest) -> dict[str, str]:
        payload = digest.to_dict()

        json_path = self.output_dir / "digest.json"
        md_path = self.output_dir / "digest.md"
        html_path = self.output_dir / "digest.html"

        with json_path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)

        md_content = self._render_markdown(payload)
        html_content = self._render_html(payload)

        md_path.write_text(md_content, encoding="utf-8")
        html_path.write_text(html_content, encoding="utf-8")

        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "html": str(html_path),
        }

    def create_api(self, digest: DailyDigest) -> FastAPI:
        app = FastAPI(title="InboxIntel Digest API", version="1.0.0")

        @app.get("/health")
        def health() -> dict[str, str]:
            return {"status": "ok"}

        @app.get("/api/digest")
        def get_digest() -> JSONResponse:
            return JSONResponse(digest.to_dict())

        @app.get("/", response_class=HTMLResponse)
        def get_html() -> HTMLResponse:
            return HTMLResponse(self._render_html(digest.to_dict()))

        return app

    def serve(self, digest: DailyDigest, host: str = "127.0.0.1", port: int = 8000) -> None:
        app = self.create_api(digest)
        uvicorn.run(app, host=host, port=port)

    def _render_markdown(self, payload: dict) -> str:
        lines = [
            "# InboxIntel Daily Intelligence Digest",
            "",
            f"- Date: {payload['email_date']}",
            f"- Source: {payload['source']}",
            f"- Generated: {payload['generated_at']}",
            "",
            "## Articles",
        ]

        if not payload["articles"]:
            lines.append("- No articles found in this run.")
            return "\n".join(lines) + "\n"

        for idx, article in enumerate(payload["articles"], start=1):
            lines.extend(
                [
                    f"### {idx}. {article['title']}",
                    f"- URL: {article['url']}",
                    f"- Publisher: {article['publisher']}",
                    f"- Published At: {article.get('published_at', '') or 'Unknown'}",
                    f"- Summary: {article.get('summary', '')}",
                    "",
                ]
            )

        return "\n".join(lines)

    def _render_html(self, payload: dict) -> str:
        cards = ""
        for article in payload["articles"]:
            cards += f"""
            <article class=\"card\">
                <h3>{article['title']}</h3>
                <p><strong>Publisher:</strong> {article['publisher']}</p>
                <p><strong>Published:</strong> {article.get('published_at', '') or 'Unknown'}</p>
                <p>{article.get('summary', '')}</p>
                <a href=\"{article['url']}\" target=\"_blank\" rel=\"noopener noreferrer\">Read article</a>
            </article>
            """

        if not cards:
            cards = "<p>No articles found in this run.</p>"

        return f"""
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>InboxIntel Digest</title>
  <style>
    :root {{
      --bg: #f6f6f2;
      --ink: #1f2421;
      --accent: #0b6e4f;
      --card: #ffffff;
      --muted: #4e5d52;
      --line: #d9e0dc;
    }}
        body {{
            margin: 0;
            font-family: "IBM Plex Sans", sans-serif;
            background: radial-gradient(circle at top, #ffffff 0%, var(--bg) 60%);
            color: var(--ink);
        }}
    .wrap {{ max-width: 980px; margin: 0 auto; padding: 2rem 1rem 3rem; }}
    h1 {{ margin: 0 0 0.75rem; font-size: clamp(1.6rem, 2.8vw, 2.4rem); }}
    .meta {{ color: var(--muted); margin-bottom: 1.25rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; }}
        .card {{
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 10px 24px rgba(16, 36, 24, 0.06);
        }}
    .card h3 {{ margin-top: 0; }}
    a {{ color: var(--accent); font-weight: 600; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <main class=\"wrap\">
    <h1>InboxIntel Daily Intelligence Digest</h1>
        <p class=\"meta\">
            Date: {payload['email_date']} | Source: {payload['source']} | Generated: {payload['generated_at']}
        </p>
    <section class=\"grid\">{cards}</section>
  </main>
</body>
</html>
        """.strip()
