# Homelab MCP Server

**Status**: Built and running, Claude Desktop connection 502 (Beads `z8c` CRITICAL)
**Created**: 2026-02-17
**Project Location**: `~/Code/homelab-mcp/`
**Beads**: `9ia` (build — CLOSED), `z8c` (connection fix — OPEN, P0)

## Overview

A custom MCP server exposing two capabilities from Claude Desktop App and n8n:
1. **Knowledge Search** — Directed search across local filesystem sources (Obsidian, AIProjects, NAS, synced cloud folders)
2. **Task Management** — Lightweight Beads CLI wrapper for creating, listing, closing, and querying tasks

Runs as SSE via Caddy HTTPS reverse proxy for Claude Desktop (via `mcp-remote`), and directly for n8n.

## Architecture

```
Mac (Claude Desktop App)                        AIServer
┌─────────────────────────┐                     ┌────────────────────────────────┐
│ Claude Desktop App      │                     │                                │
│  └─ mcp-remote          │   HTTPS (SSE)       │ Caddy (Docker)                 │
│     (npx, stdio bridge) │ ──────────────────> │  homelab-mcp.theklyx.space:443 │
│     --transport sse-only│                     │  └─ reverse_proxy ─────────────┤
│                         │                     │       192.168.1.196:3847       │
└─────────────────────────┘                     │                                │
                                                │ homelab-mcp server             │
n8n (Docker, same host)                         │  (systemd user service)        │
┌─────────────────────────┐  HTTP (SSE)         │  listening 0.0.0.0:3847        │
│ n8n MCP client          │ ──────────────────> │                                │
│ (instance-level)        │  localhost:3847     │ Knowledge + Task tools         │
└─────────────────────────┘                     │ 10 tools exposed via MCP       │
                                                └────────────────────────────────┘
```

### Connection Path (Claude Desktop → Server)

1. Claude Desktop launches `npx mcp-remote` as stdio subprocess
2. `mcp-remote` connects via HTTPS SSE to `homelab-mcp.theklyx.space/sse`
3. DNS resolves to public IP (Cloudflare DNS-only, gray cloud)
4. Request hits Caddy reverse proxy (Docker, port 443)
5. Caddy proxies to `192.168.1.196:3847` (host LAN IP)
6. homelab-mcp server handles MCP protocol via SSE transport

### Key Technical Details

- **mcp-remote transport**: Must use `--transport sse-only` (newer versions default to `http-first` which POSTs and gets 502)
- **Server binding**: Must listen on `0.0.0.0` (not localhost) for Caddy Docker container to reach it
- **Caddy SSE config**: `flush_interval -1` required for streaming, `response_header_timeout 0` for long-lived connections
- **DNS**: Cloudflare must be "DNS only" (gray cloud) — proxied mode causes ACME cert failures and 525 errors
- **TLS cert**: Let's Encrypt via Caddy auto-HTTPS, expires ~90 days, auto-renews

## Tools

### Knowledge Tools

#### `search(source, query, file_pattern?)`
Search for content across configured sources using ripgrep.
- `source`: Source name (e.g., "obsidian", "aiprojects") or "all" to search everywhere
- `query`: Search string (supports regex)
- `file_pattern`: Optional glob filter (e.g., "*.md", "**/*.yaml")
- Returns: Matching lines with file paths, line numbers, context

#### `read_file(source, path)`
Read a specific file from a source.
- `source`: Source name
- `path`: Relative path within the source
- Returns: File contents (truncated if very large)

#### `list_sources()`
List all configured knowledge sources with descriptions.
- Returns: Source names, descriptions, base paths, file counts

#### `list_files(source, path?, pattern?)`
List files in a source directory.
- `source`: Source name
- `path`: Optional subdirectory
- `pattern`: Optional glob filter
- Returns: File listing with sizes and modification dates

### Task Tools (Beads wrapper)

#### `task_list(filter?)`
List tasks with optional filtering.
- `filter`: Object with optional fields: `status` (open/in_progress/closed), `label` (e.g., "domain:infrastructure"), `priority` (0-4)
- Returns: Task list with ID, subject, status, priority, labels

#### `task_create(title, priority?, labels?, description?)`
Create a new Beads task.
- `title`: Task subject
- `priority`: 0-4 (default: 2)
- `labels`: Comma-separated labels
- `description`: Detailed description
- Returns: Created task ID and confirmation

#### `task_show(id)`
Show full details of a task.
- `id`: Beads task ID
- Returns: Full task details including description, labels, history

#### `task_update(id, status?, priority?, labels?)`
Update task properties.
- `id`: Beads task ID
- `status`: New status (open/in_progress)
- Returns: Updated task confirmation

#### `task_close(id, reason)`
Close a completed task.
- `id`: Beads task ID
- `reason`: Completion reason
- Returns: Closure confirmation

## Configuration

`~/.config/homelab-mcp/config.json`:
```json
{
  "sources": {
    "obsidian": {
      "path": "/mnt/synology_nas/Obsidian/Master",
      "description": "Personal knowledge vault — research, D&D, professional, AI, projects",
      "include": ["*.md", "*.canvas"],
      "exclude": ["@eaDir", ".obsidian", ".trash"]
    },
    "aiprojects": {
      "path": "/home/davidmoneil/AIProjects/.claude/context",
      "description": "Infrastructure documentation — systems, patterns, standards, integrations"
    },
    "knowledge": {
      "path": "/home/davidmoneil/AIProjects/knowledge",
      "description": "Reference docs, research notes, MCP documentation"
    },
    "nas": {
      "path": "/mnt/synology_nas",
      "description": "Network storage — shared files, Docker configs, backups",
      "exclude": ["@eaDir", "#recycle", "*.tmp"]
    }
  },
  "beads": {
    "project_dir": "/home/davidmoneil/AIProjects",
    "bd_path": "/home/davidmoneil/.local/bin/bd"
  },
  "search": {
    "max_results": 50,
    "context_lines": 2,
    "max_file_size_kb": 1024
  }
}
```

New sources can be added by editing the config — no code changes needed. Examples:
```json
"google_drive": {
  "path": "/home/davidmoneil/Google Drive",
  "description": "Synced Google Drive documents"
},
"onedrive": {
  "path": "/home/davidmoneil/OneDrive",
  "description": "Synced OneDrive documents"
}
```

## Tech Stack

- **Language**: TypeScript (Node.js)
- **MCP SDK**: `@modelcontextprotocol/sdk` (official)
- **Search**: ripgrep (`rg`) via child_process — fast, handles large directories
- **Transport**: stdio (Claude Desktop) + SSE (n8n) — same server, transport selected at startup
- **Task management**: Shells out to `bd` CLI (Beads)

## Claude Desktop Config (Mac)

```json
{
  "mcpServers": {
    "homelab": {
      "command": "/Users/doneil/.nvm/versions/node/v22.20.0/bin/npx",
      "args": ["-y", "mcp-remote", "https://homelab-mcp.theklyx.space/sse", "--transport", "sse-only"],
      "env": {
        "PATH": "/Users/doneil/.nvm/versions/node/v22.20.0/bin:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
      }
    }
  }
}
```

**Important**: Uses `mcp-remote` as a stdio-to-SSE bridge. The `--transport sse-only` flag is required — without it, mcp-remote tries Streamable HTTP (POST) which returns 502.

## Server (AIServer)

### Systemd Service

```bash
# Service file: ~/.config/systemd/user/homelab-mcp.service
systemctl --user status homelab-mcp    # Check status
systemctl --user restart homelab-mcp   # Restart
systemctl --user stop homelab-mcp      # Stop
journalctl --user -u homelab-mcp -f    # Logs
```

Service runs: `node ~/Code/homelab-mcp/dist/index.js --transport=sse --port=3847`

### Caddy Reverse Proxy

In `~/Docker/mydocker/caddy/Caddyfile` (~line 236):
```
homelab-mcp.theklyx.space {
    import security_filters
    reverse_proxy 192.168.1.196:3847 {
        flush_interval -1
        transport http {
            response_header_timeout 0
        }
    }
}
```

Reload after changes: `docker exec caddy caddy reload --config /etc/caddy/Caddyfile`

### DNS (Cloudflare)

- Record: `homelab-mcp.theklyx.space` → A record to public IP
- **MUST be DNS-only (gray cloud)** — proxied mode breaks ACME cert provisioning and causes 525 errors
- If cert needs renewal and is failing, temporarily verify DNS is gray-clouded

## n8n Integration

n8n connects directly (same host, no Caddy needed):
```
http://192.168.1.196:3847/sse
```

## Troubleshooting

### 502 Bad Gateway from Caddy
**Cause**: Caddy Docker container can't reach host at 192.168.1.196:3847
**Check**:
```bash
# Is server running?
systemctl --user status homelab-mcp

# Is it listening on 0.0.0.0?
ss -tlnp | grep 3847

# Can Docker reach it?
docker exec caddy wget -qO- http://192.168.1.196:3847/health

# Check Caddy error logs
docker exec caddy cat /var/log/caddy/server.log | grep homelab-mcp | tail -5
```
**Fix**: If server only on localhost, edit `index.ts` line ~522: `httpServer.listen(port, "0.0.0.0", ...)`

### 525 SSL Handshake Failed
**Cause**: Cloudflare proxy enabled (orange cloud) but Caddy doesn't have cert yet
**Fix**: Set DNS to "DNS only" (gray cloud), restart Caddy (`docker restart caddy`), wait 30s for cert

### mcp-remote "http-first" / Streamable HTTP error
**Cause**: Newer mcp-remote defaults to HTTP transport, server only supports SSE
**Fix**: Add `--transport sse-only` to args (not `sse` — valid values: `sse-only`, `http-only`, `sse-first`, `http-first`)

### mcp-remote "Non-HTTPS URLs" error
**Cause**: mcp-remote requires HTTPS for non-localhost
**Fix**: Use the Caddy HTTPS endpoint, or add `--allow-http` for LAN testing

### Connection timing issues after restart
**Cause**: mcp-remote connects before server is ready after restart
**Fix**: Wait a few seconds after `systemctl --user restart homelab-mcp`, then retry in Claude Desktop

## Security

- All source paths validated against configured base paths (no directory traversal)
- Read-only file access — no write/edit/delete operations on knowledge sources
- Beads task operations are the only write path (via `bd` CLI)
- No network access — pure local filesystem + CLI operations
- Config file specifies allowed paths; server refuses to read outside them

## Limitations (Tier 1)

- **Keyword search only** — no semantic/fuzzy search (grep-based)
- **No indexing** — searches are live filesystem scans (fast for <10K files)
- **No cross-source correlation** — searches return per-source results
- **No metadata queries** — can't answer "last file modified" type questions
- **NAS performance** — searching large NAS directories may be slower than local

## Expansion Path

| Tier | Enhancement | Trigger |
|------|-------------|---------|
| 2 | Smart routing — auto-detect best source from query | After using Tier 1 for a week |
| 3 | Vector indexing — semantic search via Ollama embeddings + LanceDB | When keyword search isn't finding things |
| 4 | Metadata indexing — file dates, names mentioned, relationships | When temporal/relational queries are needed |
