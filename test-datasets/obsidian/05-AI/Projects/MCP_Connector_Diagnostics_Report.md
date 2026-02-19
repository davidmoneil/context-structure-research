---
tags:
  - status/active
  - depth/deep
  - domain/dnd
  - domain/ai
  - domain/security
created: 2026-01-23T07:01
updated: 2026-01-24T10:38
---
# MCP Connector Diagnostics Report

**Generated:** January 23, 2026  
**Environment:** Claude.ai with Custom MCP Connectors

---

## Executive Summary

| Metric | Count |
|--------|-------|
| **Total Connectors** | 4 |
| **Connected** | 2 |
| **Errors** | 2 |
| **Pending** | 0 |

**Overall Status:** ⚠️ Partial - 50% of connectors are operational

---

## Connector Status Overview

| Connector | Status | URL | Issue |
|-----------|--------|-----|-------|
| **Klyx** | ✅ Connected | `https://n8n.theklyx.space/mcp/...` | None |
| **TheKylx-Test** | ✅ Connected | `https://n8n.theklyx.space/mcp-test/...` | None |
| **AIServerMCP** | ❌ Error | `https://192.168.1.196/sse` | Network unreachable |
| **MCP Server** | ❌ Error | `https://192.168.1.196:8080/sse` | Network unreachable |

---

## Detailed Connector Information

### 1. Klyx ✅ CONNECTED

| Property | Value |
|----------|-------|
| **Name** | Klyx |
| **Status** | 🟢 Connected |
| **URL** | `https://n8n.theklyx.space/mcp/542b3b3a-5c2e-40ea-a919-afa4ff66524c` |
| **Type** | n8n MCP (Production) |
| **Host** | n8n.theklyx.space |
| **Port** | 443 (HTTPS) |
| **Protocol** | SSE (Server-Sent Events) |
| **Path** | /mcp/ |
| **UUID** | 542b3b3a-5c2e-40ea-a919-afa4ff66524c |

**Notes:** Production n8n MCP endpoint. Endpoint is reachable and responding.

---

### 2. TheKylx-Test ✅ CONNECTED

| Property | Value |
|----------|-------|
| **Name** | TheKylx-Test |
| **Status** | 🟢 Connected |
| **URL** | `https://n8n.theklyx.space/mcp-test/542b3b3a-5c2e-40ea-a919-afa4ff66524c` |
| **Type** | n8n MCP (Test) |
| **Host** | n8n.theklyx.space |
| **Port** | 443 (HTTPS) |
| **Protocol** | SSE (Server-Sent Events) |
| **Path** | /mcp-test/ |
| **UUID** | 542b3b3a-5c2e-40ea-a919-afa4ff66524c |

**Notes:** Test environment n8n MCP endpoint. Shares the same UUID as production, differentiated by path.

---

### 3. AIServerMCP ❌ ERROR

| Property | Value |
|----------|-------|
| **Name** | AIServerMCP |
| **Status** | 🔴 Error |
| **URL** | `https://192.168.1.196/sse` |
| **Type** | Local MCP Server |
| **Host** | 192.168.1.196 |
| **Port** | 443 (HTTPS) |
| **Protocol** | SSE (Server-Sent Events) |
| **Path** | /sse |

**Error Message:**
> ⚠️ Network error - check if server is running and accessible

**Likely Causes:**
- Server is on a private/internal IP address (192.168.x.x) not reachable from the public internet
- Claude.ai runs in the cloud and cannot route to RFC 1918 private addresses
- Server may not be running
- Firewall may be blocking inbound connections on port 443

---

### 4. MCP Server ❌ ERROR

| Property | Value |
|----------|-------|
| **Name** | MCP Server |
| **Status** | 🔴 Error |
| **URL** | `https://192.168.1.196:8080/sse` |
| **Type** | Local MCP Server |
| **Host** | 192.168.1.196 |
| **Port** | 8080 |
| **Protocol** | SSE (Server-Sent Events) |
| **Path** | /sse |

**Error Message:**
> ⚠️ Network error - check if server is running and accessible

**Likely Causes:**
- Same as AIServerMCP - private IP not reachable from cloud services
- Port 8080 may be blocked by firewall
- MCP server process may not be running
- SSL/TLS certificate issues (self-signed certs)

---

## Root Cause Analysis

### Working Connectors (n8n-based)

Both **Klyx** and **TheKylx-Test** are operational because:
- They are hosted on a publicly accessible domain (`n8n.theklyx.space`)
- Valid SSL certificates (likely via Let's Encrypt or similar)
- n8n workflows are active and responding to MCP requests

### Failing Connectors (Local Server)

Both **AIServerMCP** and **MCP Server** are failing because:

1. **Private IP Address Issue**  
   `192.168.1.196` is a private RFC 1918 address that is only routable within your local network. Claude.ai operates from Anthropic's cloud infrastructure and cannot reach private IP addresses.

2. **Possible Solutions:**
   - **Option A:** Set up a reverse proxy with a public domain (e.g., via Cloudflare Tunnel, ngrok, or Tailscale Funnel)
   - **Option B:** Use Nginx Proxy Manager on your n8n server to proxy requests to the local MCP servers
   - **Option C:** Host the MCP server on a VPS with a public IP
   - **Option D:** Use Tailscale or similar mesh VPN with HTTPS endpoints

---

## Troubleshooting Commands

### Verify Local Server Status (run on your home network)

```bash
# Check if servers are listening
sudo netstat -tlnp | grep -E ':443|:8080'

# Or with ss
sudo ss -tlnp | grep -E ':443|:8080'

# Test connectivity locally
curl -v -k https://192.168.1.196/sse
curl -v -k https://192.168.1.196:8080/sse

# Check Docker containers if applicable
docker ps | grep -i mcp

# Check Portainer for container status
# (via your Portainer web UI)
```

### Verify n8n Endpoints

```bash
# Test production endpoint
curl -v https://n8n.theklyx.space/mcp/542b3b3a-5c2e-40ea-a919-afa4ff66524c

# Test staging endpoint  
curl -v https://n8n.theklyx.space/mcp-test/542b3b3a-5c2e-40ea-a919-afa4ff66524c
```

### Check SSL Certificates

```bash
# Check certificate for n8n
echo | openssl s_client -connect n8n.theklyx.space:443 2>/dev/null | openssl x509 -noout -dates

# Check local certs (if accessible)
echo | openssl s_client -connect 192.168.1.196:443 2>/dev/null | openssl x509 -noout -dates
```

---

## Recommended Actions

### Immediate (Fix Local Connectors)

1. **Option 1: Cloudflare Tunnel (Recommended)**
   ```bash
   # Install cloudflared on your server
   cloudflared tunnel create mcp-server
   cloudflared tunnel route dns mcp-server mcp.yourdomain.com
   cloudflared tunnel run --url https://localhost:443 mcp-server
   ```

2. **Option 2: Tailscale Funnel**
   ```bash
   # If Tailscale is installed
   tailscale funnel 443
   tailscale funnel 8080
   ```

3. **Option 3: Add to Nginx Proxy Manager**
   - Create new proxy host for the MCP endpoints
   - Use your existing n8n.theklyx.space or a new subdomain
   - Proxy pass to `https://192.168.1.196:443` and `:8080`

### Maintenance

- Ensure n8n workflows remain active
- Monitor SSL certificate expiration
- Set up uptime monitoring for critical endpoints

---

## Configuration Reference

### Claude.ai MCP Server Registration

These connectors are registered in Claude.ai's settings and will be available for use in artifacts that call the Anthropic API with the `mcp_servers` parameter:

```javascript
mcp_servers: [
  {
    "type": "url",
    "url": "https://n8n.theklyx.space/mcp/542b3b3a-5c2e-40ea-a919-afa4ff66524c",
    "name": "Klyx"
  },
  {
    "type": "url", 
    "url": "https://n8n.theklyx.space/mcp-test/542b3b3a-5c2e-40ea-a919-afa4ff66524c",
    "name": "TheKylx-Test"
  },
  {
    "type": "url",
    "url": "https://192.168.1.196/sse",
    "name": "AIServerMCP"
  },
  {
    "type": "url",
    "url": "https://192.168.1.196:8080/sse", 
    "name": "MCP Server"
  }
]
```

---

## Appendix: Test Results Raw Data

**Test Date:** January 23, 2026  
**Test Method:** Browser-based fetch with 5-second timeout  
**Test Source:** Claude.ai diagnostic artifact

| Connector | HTTP Response | Latency | Error |
|-----------|--------------|---------|-------|
| Klyx | OK (no-cors) | <5s | None |
| TheKylx-Test | OK (no-cors) | <5s | None |
| AIServerMCP | Failed | Timeout | Network error |
| MCP Server | Failed | Timeout | Network error |

---

*Report generated by Claude for iCIMS CISO troubleshooting*
