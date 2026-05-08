# DuckDuckGo Search MCP Server

A Model Context Protocol (MCP) server that provides web search capabilities through DuckDuckGo.

---

## Способ 1: через `uvx`

Если пакет опубликован на PyPI (вашего registry):

```json
{
    "mcpServers": {
        "ddg-search": {
            "command": "uvx",
            "args": ["duckduckgo-mcp-server"]
        }
    }
}
```

---

## Альтернативный способ

### 1. Клонирование репозитория

```bash
# Клонируй репозиторий
git clone <репозиторий>
cd duckduckgo-mcp-server
```

### 2. Установка зависимостей

```bash
# Установи зависимости через uv
uv sync
```

### 3. Проверка работоспособности

Запусти сервер в терминале для проверки:

```bash
cd /path/to/duckduckgo-mcp-server
source .venv/bin/activate
python -m duckduckgo_mcp_server.server --transport stdio
```

**Нажми `Ctrl+C` для остановки.** После проверки сервер больше не нужно запускать вручную — он будет запускаться автоматически через настройки GigaCode.

### 2. Настройка Claude Desktop

Создай или отредактируй файл конфигурации:
`mcp_settings.json`

```json
{
    "mcpServers": {
        "ddg-search": {
            "type": "stdio",
            "command": "/path/to/duckduckgo-mcp-server/.venv/bin/python",
            "args": ["-m", "duckduckgo_mcp_server.server", "--transport", "stdio"]
        }
    }
}
```

## Переменные окружения (опционально)

```json
{
    "mcpServers": {
        "ddg-search": {
            "type": "stdio",
            "command": "/path/to/duckduckgo-mcp-server/.venv/bin/python",
            "args": ["-m", "duckduckgo_mcp_server.server", "--transport", "stdio"],
            "env": {
                "DDG_SAFE_SEARCH": "MODERATE",
                "MCP_LOG_LEVEL": "INFO"
            }
        }
    }
}
```

| Переменная | Значения | По умолчанию |
|------------|----------|--------------|
| `DDG_SAFE_SEARCH` | `STRICT`, `MODERATE`, `OFF` | `MODERATE` |
| `DDG_REGION` | `us-en`, `cn-zh`, `jp-ja` | (нет) |
| `DDG_VERIFY_SSL` | `true`, `false` | `false` (для корпоративных сетей) |
| `MCP_LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` |

---

## Решение проблем

Если при запуске через
```json
{
    "mcpServers": {
        "ddg-search": {
            "command": "uvx",
            "args": ["duckduckgo-mcp-server"]
        }
    }
}
```

Агенту в ответ от сервера будет всё время приходить: `No results were found`, то скорее всего ошибка из-за корпоративных сетей. Попробуйте клонировать репозиторий и использовать его. В нём есть фикс этой проблемы

**Сервер не запускается** — убедись, что активировал виртуальное окружение: `source .venv/bin/activate`
