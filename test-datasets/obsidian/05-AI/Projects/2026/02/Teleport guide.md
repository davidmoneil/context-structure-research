
# Teleport Community Edition: Complete Deployment Guide

## Browser-Based SSH Access for Your AI Server — Zero VPN, Zero Inbound Ports

-----

## 1. What Is Teleport?

Teleport is an open-source, zero-trust access gateway built by Gravitational (now Teleport Inc.). It replaces traditional SSH key management, VPNs, and bastion hosts with a single, identity-aware platform that provides browser-based and CLI access to your infrastructure.

Instead of managing SSH keys, opening firewall ports, or maintaining always-on VPN tunnels, Teleport issues **short-lived certificates** tied to your identity. When they expire, access is revoked automatically — no key rotation, no credential sprawl, no forgotten service accounts.

At its core, Teleport is a single Go binary that runs three services:

|Service                |Role                                                                                                                   |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------|
|**Auth Service**       |Certificate authority — issues and validates short-lived certs for users and hosts                                     |
|**Proxy Service**      |Identity-aware reverse proxy — terminates TLS, serves the Web UI, and routes all protocol traffic (SSH, HTTPS, K8s, DB)|
|**SSH Service (Agent)**|Runs on each target host — registers with the Auth Service and accepts certificate-based SSH connections               |

### How a Connection Works

1. You open a browser and navigate to `https://teleport.yourdomain.com`
2. Teleport prompts you for credentials + MFA (WebAuthn/TOTP)
3. Upon successful auth, the Auth Service issues a short-lived certificate (default: 12 hours)
4. The Web UI presents a list of servers registered in your cluster
5. You click a server → a full interactive terminal opens in your browser
6. The session is recorded, auditable, and can be replayed later

No SSH keys were exchanged. No ports were opened on the target server. No VPN was involved.

-----

## 2. Why Teleport for a Home Lab / AI Server

### The Problem

You have an AI server at home (likely running Docker containers, n8n workflows, GPU workloads). You want to SSH into it from anywhere — a hotel in Hyderabad, an airport lounge in Amsterdam, your phone — without:

- Maintaining a VPN that drains battery and adds latency
- Opening SSH port 22 (or any port) on your firewall
- Managing SSH keys across multiple devices
- Worrying about credential theft on untrusted networks

### What Teleport Gives You

- **Browser-based SSH terminal** — no client software needed on the connecting device
- **Certificate-based auth** — no static SSH keys, no passwords stored anywhere
- **Mandatory MFA** — WebAuthn (hardware key) or TOTP (authenticator app) enforced by default
- **Session recording and replay** — every keystroke captured for audit
- **RBAC** — define who can access which servers with which Linux user accounts
- **Persistent sessions** — reconnect to active sessions if your browser disconnects
- **Session sharing** — share a live terminal with another user for collaborative troubleshooting
- **Audit log** — every auth attempt, session start/stop, and file transfer logged
- **CLI access via `tsh`** — when you’re on a trusted device, use the Teleport CLI for native SSH-like experience
- **No inbound ports** — when paired with Cloudflare Tunnel, your server makes only outbound connections

### Licensing Note

Teleport Community Edition underwent a license change in 2024. Starting with version 16, Community Edition uses a commercial license that is **free for organizations with fewer than 100 employees and less than $10M in revenue**. For personal/home lab use, this is completely fine. However, be aware:

- The open-source (AGPL) versions are prior to v16
- SSO integration (beyond GitHub) requires Enterprise
- Some advanced features (Access Requests, Device Trust enforcement) are Enterprise-only
- For your use case (personal AI server access), Community Edition has everything you need

-----

## 3. Architecture for Your Setup

Here’s the target architecture — zero inbound ports, enterprise-grade security:

```
┌──────────────────────────────────────────────────────┐
│  YOUR BROWSER (anywhere in the world)                │
│  https://teleport.yourdomain.com                     │
└──────────────┬───────────────────────────────────────┘
               │ HTTPS (443)
               ▼
┌──────────────────────────────────────────────────────┐
│  CLOUDFLARE EDGE (global CDN)                        │
│  - DDoS protection                                   │
│  - TLS termination                                   │
│  - WAF rules (optional)                              │
└──────────────┬───────────────────────────────────────┘
               │ Cloudflare Tunnel (outbound only)
               ▼
┌──────────────────────────────────────────────────────┐
│  YOUR HOME NETWORK (behind UniFi firewall)           │
│                                                      │
│  ┌─────────────────────────────────────────────────┐ │
│  │  Docker Host (AI Server)                        │ │
│  │                                                 │ │
│  │  ┌───────────────┐  ┌────────────────────────┐  │ │
│  │  │  cloudflared   │  │  Teleport Container    │  │ │
│  │  │  (tunnel)      │──│  - Auth Service        │  │ │
│  │  │                │  │  - Proxy Service       │  │ │
│  │  └───────────────┘  │  - SSH Service          │  │ │
│  │                     │  - Web UI (:3080)       │  │ │
│  │                     └────────────────────────┘  │ │
│  │                                                 │ │
│  │  ┌───────────────┐  ┌────────────────────────┐  │ │
│  │  │  n8n           │  │  Other containers      │  │ │
│  │  │  GPU workloads │  │  (optional agents)     │  │ │
│  │  └───────────────┘  └────────────────────────┘  │ │
│  └─────────────────────────────────────────────────┘ │
│                                                      │
│  FIREWALL: Zero inbound ports open                   │
│  All traffic flows outbound via Cloudflare Tunnel    │
└──────────────────────────────────────────────────────┘
```

### Traffic Flow

1. **cloudflared** (running in Docker) establishes an outbound-only encrypted tunnel to Cloudflare’s edge network on port 7844
2. Your DNS record (`teleport.yourdomain.com`) points to Cloudflare (orange-clouded)
3. When you browse to the URL, Cloudflare routes the request through the tunnel to your Teleport Proxy Service
4. Teleport handles authentication, MFA, and certificate issuance
5. Your SSH session runs over WebSocket through the same HTTPS connection

**Result:** Your home IP is never exposed. Your firewall has zero inbound rules. All traffic is encrypted end-to-end.

-----

## 4. Prerequisites

Before starting, ensure you have:

|Requirement                |Details                                                                                      |
|---------------------------|---------------------------------------------------------------------------------------------|
|**Docker & Docker Compose**|v2.x+ on your AI server                                                                      |
|**A domain name**          |Any domain you control (e.g., `yourdomain.com`)                                              |
|**Cloudflare account**     |Free tier is sufficient — domain’s DNS must be managed by Cloudflare                         |
|**Cloudflare Tunnel token**|Created via the Zero Trust dashboard                                                         |
|**Linux user accounts**    |The users Teleport will SSH as must exist on the host (e.g., `root`, `claude`, your username)|
|**TOTP authenticator app** |Google Authenticator, Authy, 1Password, etc.                                                 |

-----

## 5. Step-by-Step Deployment

### Step 1: Create Directory Structure

```bash
mkdir -p ~/teleport/{config,data}
cd ~/teleport
```

### Step 2: Generate Teleport Configuration

Since you’re running behind Cloudflare Tunnel (which terminates TLS), you’ll use Teleport’s self-signed certificate mode with `proxy_listener_mode: multiplex` disabled.

Create `~/teleport/config/teleport.yaml`:

```yaml
version: v3
teleport:
  nodename: ai-server
  data_dir: /var/lib/teleport
  log:
    output: stderr
    severity: INFO

auth_service:
  enabled: true
  listen_addr: 0.0.0.0:3025
  cluster_name: teleport.yourdomain.com
  tokens:
    - proxy,node:your-secure-join-token-here
  authentication:
    type: local
    second_factor: "on"          # Enforces MFA (TOTP or WebAuthn)
    webauthn:
      rp_id: teleport.yourdomain.com

proxy_service:
  enabled: true
  listen_addr: 0.0.0.0:3023
  web_listen_addr: 0.0.0.0:3080
  tunnel_listen_addr: 0.0.0.0:3024
  public_addr: teleport.yourdomain.com:443
  # Since Cloudflare terminates TLS, we use self-signed certs internally
  # and tell cloudflared to skip TLS verification to the origin
  acme: {}

ssh_service:
  enabled: true
  listen_addr: 0.0.0.0:3022
  labels:
    env: homelab
    role: ai-server
  commands:
    - name: hostname
      command: [hostname]
      period: 1m0s
    - name: uptime
      command: [uptime, -p]
      period: 5m0s
```

**Important notes on this config:**

- `second_factor: "on"` — MFA is mandatory. Teleport v16+ refuses to start without it.
- `public_addr` uses port 443 because that’s what users see via Cloudflare
- The `tokens` field is a static join token for simplicity — in production, use short-lived tokens via `tctl tokens add`
- `labels` let you tag and filter servers in the Web UI

### Step 3: Create Docker Compose File

Create `~/teleport/docker-compose.yml`:

```yaml
services:
  teleport:
    image: public.ecr.aws/gravitational/teleport-distroless:18.6.1
    container_name: teleport
    hostname: teleport.yourdomain.com
    entrypoint: ["/usr/local/bin/teleport", "start", "-c", "/etc/teleport/teleport.yaml"]
    ports:
      - "3080:3080"    # Web UI
      - "3023:3023"    # SSH proxy
      - "3024:3024"    # Reverse tunnel
      - "3025:3025"    # Auth
      - "3022:3022"    # SSH node
    volumes:
      - ./config:/etc/teleport
      - ./data:/var/lib/teleport
    restart: unless-stopped
    networks:
      - teleport-net

  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: cloudflared
    command: tunnel run
    environment:
      - TUNNEL_TOKEN=your-cloudflare-tunnel-token-here
    restart: unless-stopped
    networks:
      - teleport-net
    depends_on:
      - teleport

networks:
  teleport-net:
    driver: bridge
```

### Step 4: Configure Cloudflare Tunnel

In the Cloudflare Zero Trust dashboard:

1. Go to **Networks → Tunnels → Create a tunnel**
2. Name it (e.g., `homelab-teleport`)
3. Copy the tunnel token — paste it into the `TUNNEL_TOKEN` environment variable in docker-compose.yml
4. Configure the **Public Hostname**:

|Field       |Value                                |
|------------|-------------------------------------|
|Subdomain   |`teleport`                           |
|Domain      |`yourdomain.com`                     |
|Service Type|`HTTPS`                              |
|URL         |`teleport:3080` (Docker service name)|

1. Under **Additional Settings** for this route:
- **No TLS Verify:** `ON` — This tells cloudflared to accept Teleport’s self-signed cert
- **HTTP Host Header:** `teleport.yourdomain.com`
1. **SSL/TLS Settings** for your domain in Cloudflare:
- Set encryption mode to **Full** (not Full Strict, since Teleport uses a self-signed cert)

### Step 5: Launch the Stack

```bash
cd ~/teleport
docker compose up -d
```

Verify both containers are running:

```bash
docker compose ps
docker compose logs -f teleport
```

Wait for the Teleport log line: `Teleport is ready to serve connections`

### Step 6: Create Your Admin User

```bash
docker compose exec teleport tctl users add admin \
  --roles=editor,access \
  --logins=root,yourusername
```

This outputs a one-time registration URL. Open it in your browser at:

```
https://teleport.yourdomain.com/web/invite/<token>
```

You’ll be prompted to:

1. Set a password
2. Enroll an MFA device (scan QR code with your authenticator app)

### Step 7: Verify Access

1. Navigate to `https://teleport.yourdomain.com`
2. Log in with your credentials + MFA
3. You should see your AI server listed in the **Servers** tab
4. Click **Connect** → select a Linux user → a terminal opens in your browser

-----

## 6. Key Features Deep Dive

### Browser-Based Terminal

The Web UI provides a full `xterm.js`-based terminal that supports:

- Copy/paste (mouse-based)
- Terminal resize
- Color and Unicode support
- Multiple simultaneous sessions in browser tabs
- Session persistence — if your browser disconnects, the session continues server-side and you can reconnect

### Session Recording and Replay

Every interactive session is recorded by default. To review:

- **Web UI:** Go to **Session Recordings** → click any session to replay
- **CLI:** `tsh recordings ls` then `tsh play <session-id>`
- Recordings capture both input and output with timestamps
- Teleport 18.2+ includes AI-generated session summaries

### Role-Based Access Control (RBAC)

Define granular access with Teleport roles:

```yaml
# Example: Read-only access for a family member
kind: role
version: v7
metadata:
  name: family-readonly
spec:
  allow:
    logins: ['observer']        # Limited Linux user
    node_labels:
      env: homelab
    rules:
      - resources: [session]
        verbs: [list, read]     # Can view but not create sessions
  options:
    max_session_ttl: 4h         # Cert expires after 4 hours
    record_session:
      default: best_effort
```

Apply with: `tctl create -f role.yaml`

### Audit Log

Every event is captured:

- Authentication attempts (success and failure)
- Session starts, stops, and joins
- File transfers
- Commands executed (with eBPF enhanced recording if enabled)
- User role changes

View via Web UI under **Audit Log** or query via `tctl`:

```bash
docker compose exec teleport tctl events ls
```

### CLI Access with `tsh`

When you’re on a trusted device (e.g., your laptop), install the `tsh` client for a native SSH experience:

```bash
# Login (opens browser for MFA)
tsh login --proxy=teleport.yourdomain.com

# List servers
tsh ls

# SSH into a server
tsh ssh yourusername@ai-server

# SCP file transfer
tsh scp localfile.txt yourusername@ai-server:/path/to/dest

# Port forward
tsh ssh -L 8080:localhost:8080 yourusername@ai-server
```

Certificates are cached locally and auto-expire. No SSH keys involved.

-----

## 7. Adding Additional Nodes

To add other machines in your home lab to the Teleport cluster:

### Option A: Install the Teleport Agent

On the target host:

```bash
# Install Teleport binary
curl https://cdn.teleport.dev/install.sh | bash -s 18.6.1

# Join the cluster
teleport start \
  --roles=node \
  --token=your-secure-join-token-here \
  --auth-server=teleport.yourdomain.com:443 \
  --labels="env=homelab,role=media-server"
```

### Option B: Agentless Mode (OpenSSH)

If you don’t want to install Teleport on every host, you can use agentless mode with existing OpenSSH servers. This proxies SSH through Teleport without replacing `sshd`.

-----

## 8. Security Hardening Checklist

Since you’re exposing this to the internet (via Cloudflare), lock it down:

|Item                            |Action                                                                     |
|--------------------------------|---------------------------------------------------------------------------|
|**MFA Enforcement**             |Already enforced by default in v16+ — verify with `tctl get cap`           |
|**Short certificate TTL**       |Set `max_session_ttl: 8h` in your roles                                    |
|**Disable password-only auth**  |Teleport enforces MFA by default; don’t weaken this                        |
|**Restrict logins**             |Only allow specific Linux users per role — never blanket `root` access     |
|**Session recording**           |Enabled by default — ensure recordings persist (mount a durable volume)    |
|**Cloudflare WAF**              |Enable basic WAF rules on the tunnel route                                 |
|**Cloudflare Access (optional)**|Add an additional authentication layer before traffic even reaches Teleport|
|**Rate limiting**               |Cloudflare provides this automatically                                     |
|**Update regularly**            |Subscribe to Teleport’s release RSS for security patches                   |
|**UniFi firewall**              |Verify zero inbound port forwards exist for the Teleport host              |
|**Separate Docker network**     |Teleport runs on its own bridge network (already configured above)         |

-----

## 9. Maintenance and Operations

### Upgrading Teleport

```bash
cd ~/teleport

# Update the image tag in docker-compose.yml to the new version
# Then:
docker compose pull teleport
docker compose up -d teleport
```

**Important:** Teleport must be upgraded one major version at a time (e.g., 17 → 18, not 16 → 18).

### Backup

Your critical data is in `~/teleport/data/`. Back up regularly:

```bash
# Stop teleport briefly for consistent backup
docker compose stop teleport
tar czf teleport-backup-$(date +%Y%m%d).tar.gz data/
docker compose start teleport
```

### Monitoring

Check cluster health:

```bash
docker compose exec teleport tctl status
docker compose exec teleport tctl nodes ls
docker compose exec teleport tctl users ls
```

### Rotating the Join Token

```bash
# Generate a new short-lived token
docker compose exec teleport tctl tokens add --type=node --ttl=1h
```

-----

## 10. Comparison: Teleport vs. Alternatives

|Feature            |Teleport CE           |Apache Guacamole  |Wetty/ttyd       |VPN (WireGuard)    |
|-------------------|----------------------|------------------|-----------------|-------------------|
|Browser SSH        |✅ Full xterm.js       |✅ Full terminal   |✅ Basic          |❌ Requires client  |
|Certificate auth   |✅ Auto-rotating       |❌ Password/LDAP   |❌ None           |✅ Key-based        |
|MFA                |✅ WebAuthn + TOTP     |✅ TOTP only       |❌ None built-in  |❌ None built-in    |
|Session recording  |✅ Full replay         |✅ Full replay     |❌ None           |❌ None             |
|RBAC               |✅ Fine-grained        |✅ Connection-level|❌ None           |❌ Network-level    |
|Audit log          |✅ Comprehensive       |✅ Basic           |❌ None           |❌ None             |
|Persistent sessions|✅ Reconnectable       |✅ Reconnectable   |❌ Lost on refresh|N/A                |
|Protocol support   |SSH, K8s, DB, Web, RDP|SSH, RDP, VNC     |SSH only         |All (network-level)|
|Zero-trust model   |✅ Identity-based      |❌ Network-based   |❌ None           |❌ Network-based    |
|Complexity         |Medium                |Medium            |Low              |Low                |

-----

## 11. Troubleshooting

**Can’t reach the Web UI through Cloudflare:**

- Verify cloudflared container is running: `docker compose logs cloudflared`
- Check Cloudflare Tunnel status in Zero Trust dashboard → Connectors
- Ensure “No TLS Verify” is enabled on the tunnel route
- Confirm DNS record exists and is orange-clouded (proxied)

**MFA enrollment fails:**

- Ensure your system clock is accurate (NTP synced) — TOTP codes are time-sensitive
- Try a different authenticator app
- Check Teleport logs: `docker compose logs teleport | grep auth`

**“Access denied” when connecting to a server:**

- Verify the Linux user exists on the target host: `id yourusername`
- Check your Teleport role allows that login: `tctl get roles`
- Verify the role’s `node_labels` match the server’s labels

**Sessions disconnect frequently:**

- Check Cloudflare tunnel stability in the dashboard
- Increase WebSocket timeout in Cloudflare: Origin Rules → WebSocket timeout
- Verify your home internet connection stability

-----

## 12. Quick Reference Commands

```bash
# User management
tctl users ls                           # List users
tctl users add <name> --roles=access    # Add user
tctl users rm <name>                    # Remove user
tctl users reset <name>                 # Reset MFA

# Node management
tctl nodes ls                           # List registered nodes
tctl tokens add --type=node --ttl=1h    # Generate join token

# Session management
tctl recordings ls                      # List session recordings

# Cluster status
tctl status                             # Cluster health
tctl get cap                            # Auth preferences (MFA settings)

# Role management
tctl get roles                          # List all roles
tctl create -f role.yaml                # Create/update role
```

-----

## References

- [Teleport Documentation](https://goteleport.com/docs/)
- [Teleport Community Edition Download](https://goteleport.com/download/)
- [Teleport Docker Installation](https://goteleport.com/docs/installation/docker/)
- [Cloudflare Tunnel Setup](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)
- [Teleport + Cloudflare Tunnel Discussion](https://github.com/gravitational/teleport/discussions/50346)
- [Teleport GitHub Repository](https://github.com/gravitational/teleport)