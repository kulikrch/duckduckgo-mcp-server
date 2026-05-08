# DuckDuckGo MCP Server

## Project Overview

This is a **Model Context Protocol (MCP) server** that provides web search capabilities through DuckDuckGo, with additional features for content fetching and parsing. Built with Python using the FastMCP framework, it exposes two primary tools: `search` (web search) and `fetch_content` (webpage content extraction).

**Key Technologies:**
- Python 3.10+ (tested through 3.14)
- FastMCP framework (`mcp[cli]`)
- HTTP client: `httpx` (with optional `curl_cffi` browser impersonation backend)
- HTML parsing: `beautifulsoup4`
- Build system: Hatchling
- Package manager: UV

**Project Type:** Python package / MCP server

## Architecture

The server consists of three main components in `src/duckduckgo_mcp_server/server.py`:

| Component | Purpose |
|-----------|---------|
| `RateLimiter` | Sliding-window rate limiter (30 req/min for search, 20 req/min for content fetching) |
| `DuckDuckGoSearcher` | Scrapes DuckDuckGo's HTML endpoint, parses results with BeautifulSoup, handles SafeSearch (`kp` param) and region (`kl` param) configuration |
| `WebContentFetcher` | Fetches arbitrary URLs, strips non-content elements (script, style, nav, header, footer), returns cleaned text truncated to 8000 chars |

### Two MCP Tools

1. **`search`**: Web search via DuckDuckGo
   - Parameters: `query` (required), `max_results` (1-20, default 10), `region` (optional, e.g., `us-en`, `jp-ja`)
   - Returns formatted results with titles, URLs, and snippets

2. **`fetch_content`**: Webpage content extraction
   - Parameters: `url` (required), `start_index` (pagination offset), `max_length` (max chars, default 8000), `backend` (optional override)
   - Backend options: `httpx` (default, lightweight), `curl` (Chrome TLS impersonation), `auto` (try httpx, fall back on 403/challenge)

## Building and Running

### Installation & Setup

```bash
# Install dependencies
uv sync

# Build package (for publishing)
uv build
```

### Running the Server

```bash
# Run with stdio transport (default, for Claude Desktop/Code)
uv run duckduckgo-mcp-server

# Run with MCP Inspector (interactive testing)
mcp dev src/duckduckgo_mcp_server/server.py

# Run locally for Claude Desktop
mcp install src/duckduckgo_mcp_server/server.py

# Run with alternative transports
uv run duckduckgo-mcp-server --transport sse
uv run duckduckgo-mcp-server --transport streamable-http

# With custom backend (requires [browser] extra)
uv run duckduckgo-mcp-server --fetch-backend curl
uv run duckduckgo-mcp-server --fetch-backend auto
```

### CLI Options

| Flag | Description |
|------|-------------|
| `--transport` | `stdio` (default), `sse`, or `streamable-http` |
| `--fetch-backend` | `httpx` (default), `curl`, or `auto` (requires `[browser]` extra) |
| `--host` | Bind address for SSE/streamable-http (default: `127.0.0.1`) |
| `--port` | Bind port for SSE/streamable-http (default: `8000`) |

### Environment Variables

| Variable | Values | Description |
|----------|--------|-------------|
| `DDG_SAFE_SEARCH` | `STRICT`, `MODERATE` (default), `OFF` | SafeSearch filtering level (fixed at startup) |
| `DDG_REGION` | e.g., `us-en`, `cn-zh`, `jp-ja`, `wt-wt` | Default region/language code (fixed at startup) |
| `DDG_VERIFY_SSL` | `true`, `false` (default: `false`) | SSL certificate verification. Default `false` for corporate proxy support. Set `true` if you need strict SSL verification. |

## Testing

```bash
# Run all tests (unit + e2e)
uv run python -m pytest src/duckduckgo_mcp_server/ -v

# Unit tests only
uv run python -m pytest src/duckduckgo_mcp_server/test_server.py -v

# E2E tests only
uv run python -m pytest src/duckduckgo_mcp_server/test_e2e.py -v

# Single test
uv run python -m pytest src/duckduckgo_mcp_server/test_server.py::TestRateLimiter::test_acquire_removes_expired_entries
```

**Test Structure:**
- `test_server.py`: 21 unit tests using `unittest.mock.patch` to mock httpx
- `test_e2e.py`: 4 MCP protocol e2e tests using `pytest-asyncio` with in-memory MCP client/server

## Development Conventions

**Code Style & Patterns:**
- Async-first with `asyncio`/`httpx`
- Type hints throughout (using `typing.List`, `typing.Dict`, `Optional`, etc.)
- Comprehensive error handling with MCP context logging (`ctx.info()`, `ctx.error()`)
- Dataclasses for structured data (`SearchResult`)
- Enum for SafeSearch modes

**Error Handling:**
- HTTP timeouts → `httpx.TimeoutException`
- HTTP errors → `httpx.HTTPError`
- Unexpected errors → caught, logged via `ctx.error()`, stack trace printed to stderr

**Rate Limiting:**
- Search: 30 requests per minute
- Content fetching: 20 requests per minute
- Sliding window implementation with automatic wait time calculation

**HTML Parsing:**
- DuckDuckGo results parsed from `.result` CSS selectors
- Ads filtered by `y.js` in link
- Redirect URLs cleaned up
- Content extraction removes `script`, `style`, `nav`, `header`, `footer` elements

## Optional Features

### Browser Backend (`[browser]` extra)

Some sites block the default `httpx` client due to TLS fingerprinting. The optional `curl` backend impersonates Chrome 131:

```bash
# Install with browser support
uv pip install "duckduckgo-mcp-server[browser]"

# Use curl backend for fetch_content
uv run duckduckgo-mcp-server --fetch-backend curl

# Or per-call override in fetch_content
fetch_content(url, backend="curl")
```

### Docker Deployment

```bash
# Build
docker build -t duckduckgo-mcp-server .

# Run (stdio via stdin/stdout)
docker run -i --rm duckduckgo-mcp-server

# Run with SSE (expose port)
docker run -p 8000:8000 duckduckgo-mcp-server --transport sse --host 0.0.0.0 --port 8000
```

## Configuration for MCP Clients

### Claude Desktop

```json
{
    "mcpServers": {
        "ddg-search": {
            "command": "uvx",
            "args": ["duckduckgo-mcp-server"],
            "env": {
                "DDG_SAFE_SEARCH": "STRICT",
                "DDG_REGION": "cn-zh"
            }
        }
    }
}
```

### Claude Code

```bash
claude mcp add ddg-search uvx duckduckgo-mcp-server
```

## Publishing

```bash
# Build and publish to PyPI
uv build
# Then: twine upload dist/*
```

Package name on PyPI: `duckduckgo-mcp-server`

## CI/CD

GitHub Actions (`.github/workflows/test.yml`) runs tests on Python 3.10–3.14 using `astral-sh/setup-uv`.

---

**Note for GigaCode:** When working with this project, respect the existing architecture—don't modify the FastMCP tool decorators without understanding how they expose tools to MCP clients. Test changes thoroughly, especially rate limiting and error handling paths. The server uses `uv` as its package manager (not `pip` or `poetry`).
