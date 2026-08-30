# Ask Jarvis web client

This dependency-free page calls the n8n router webhook and formats single-agent
and multi-agent responses.

## Run locally

Serve this folder with any static HTTP server, then open the printed URL. The
easiest Windows option is the VS Code **Live Server** extension: right-click
`index.html`, select **Open with Live Server**, and use the URL it opens. Avoid
opening `index.html` directly with `file://`, because browsers may block the
cross-origin webhook request.

Example with Python:

```powershell
python -m http.server 8080 --directory web-client
```

Then open `http://localhost:8080` and set the Connection URL to the n8n Test or
Production webhook.

For local development, configure the n8n Webhook node's allowed origins to
include `http://localhost:8080` (or use `*` only for local testing).
