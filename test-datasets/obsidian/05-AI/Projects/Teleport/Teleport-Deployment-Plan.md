---
tags: [infrastructure, security, remote-access, teleport, cloudflare]
status: planned
priority: P1-HIGH
beads_id: AIProjects-aay
created: 2026-02-08
---

# Teleport CE Deployment Plan

**Goal**: Browser-based SSH into AIServer from anywhere - zero VPN, zero inbound ports, zero SSH keys.

**Source Guide**: [[teleport-guide.pdf]] (in `06-Sessions/2026/02-Feb/`)

---

## Quick Summary

| Item | Value |
|------|-------|
| **Software** | Teleport Community Edition v18.6.1 |
| **Subdomain** | `teleport.theklyx.space` |
| **Deploy location** | `~/Docker/mydocker/teleport/` |
| **Access method** | Browser only (no tsh CLI) |
| **Containers** | 2 (teleport + cloudflared) |
| **Inbound ports** | Zero (Cloudflare Tunnel is outbound-only) |
| **Cost** | Free (CE license, Cloudflare free tier) |
| **Beads task** | `AIProjects-aay` |

---

## Architecture

```
YOUR BROWSER (anywhere)
  https://teleport.theklyx.space
            |
            | HTTPS (443)
            v
  CLOUDFLARE EDGE (global CDN)
  - DDoS protection
  - TLS termination
  - WAF rules (optional)
            |
            | Cloudflare Tunnel (outbound only)
            v
  AIServer (192.168.1.196)
  +-----------------------------------------+
  |  Docker Host                            |
  |                                         |
  |  +-------------+  +------------------+ |
  |  | cloudflared |--| Teleport         | |
  |  | (tunnel)    |  | - Auth Service   | |
  |  +-------------+  | - Proxy Service  | |
  |                    | - SSH Service    | |
  |                    | - Web UI (:3080) | |
  |                    +------------------+ |
  |                                         |
  |  FIREWALL: Zero inbound ports open      |
  |  All traffic flows outbound via tunnel  |
  +-----------------------------------------+
```

**Key point**: This is completely separate from Caddy. Caddy handles `n8n.theklyx.space`, `chat.theklyx.space`, etc. via Cloudflare DNS proxying + port 443. Teleport uses a Cloudflare Tunnel (outbound connection from AIServer) - no port forwarding, no firewall changes.

---

## Phase 0: Cloudflare Zero Trust Setup

> **This is manual - you must do this in a browser.**

### Step 1: Access Zero Trust Dashboard

1. Go to **https://one.dash.cloudflare.com**
2. If first time: set up Zero Trust account (free tier, no credit card needed)
3. Choose a team name (e.g., `moneil-homelab`)

### Step 2: Create a Tunnel

1. Navigate to **Networks > Tunnels**
2. Click **Create a tunnel**
3. Select **Cloudflared** connector type
4. Name it: `homelab-teleport`
5. **Copy the tunnel token** - it looks like `eyJhIjoiNzM...` (long string)
6. Save this token - you'll need it for the `.env` file

### Step 3: Configure Public Hostname

In the tunnel configuration, add a **Public Hostname**:

| Field | Value |
|-------|-------|
| Subdomain | `teleport` |
| Domain | `theklyx.space` |
| Service Type | `HTTPS` |
| URL | `teleport:3080` |

> The URL is the Docker service name, not a public URL. cloudflared connects to it over the Docker network.

### Step 4: Additional Settings

Under **Additional Settings** for this route:

- **No TLS Verify**: `ON` (Teleport uses self-signed certs internally since Cloudflare handles public TLS)
- **HTTP Host Header**: `teleport.theklyx.space`

### Step 5: SSL/TLS Mode

Go to your **theklyx.space** zone settings in Cloudflare:

- **SSL/TLS > Overview**: Verify encryption mode
- For the Teleport route, **Full** mode works (not Full Strict, since Teleport uses self-signed certs)
- Your existing Caddy subdomains use Let's Encrypt so they work with Full Strict
- If you're currently on Full Strict globally, you may need to create a **Configuration Rule** for `teleport.theklyx.space` to use Full mode

> **Checkpoint**: After this phase, the tunnel should show as "Healthy" in the Zero Trust dashboard (even before Teleport is running, the tunnel status will show once cloudflared connects).

---

## Phase 1: Create Config Files

> **Claude can do this phase.** Just say "set up Phase 1 for Teleport" in a session.

### Directory Structure

```bash
mkdir -p ~/Docker/mydocker/teleport/{config,data}
cd ~/Docker/mydocker/teleport
```

### File: `.env`

```bash
# Cloudflare Tunnel token from Phase 0
TUNNEL_TOKEN=your-token-here

# Teleport join token (change this to something secure)
TELEPORT_JOIN_TOKEN=change-me-to-a-secure-random-string
```

### File: `.gitignore`

```
.env
data/
```

### File: `config/teleport.yaml`

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
  cluster_name: teleport.theklyx.space
  tokens:
    - proxy,node:${TELEPORT_JOIN_TOKEN}
  authentication:
    type: local
    second_factor: "on"           # Enforces MFA (TOTP or WebAuthn)
    webauthn:
      rp_id: teleport.theklyx.space

proxy_service:
  enabled: true
  listen_addr: 0.0.0.0:3023
  web_listen_addr: 0.0.0.0:3080
  tunnel_listen_addr: 0.0.0.0:3024
  public_addr: teleport.theklyx.space:443
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
- `second_factor: "on"` = MFA is mandatory (Teleport v16+ refuses to start without it)
- `public_addr` uses port 443 because that's what users see via Cloudflare
- The `tokens` field is a static join token for simplicity - rotate it after first boot
- `labels` let you tag and filter servers in the Web UI

### File: `docker-compose.yml`

```yaml
services:
  teleport:
    image: public.ecr.aws/gravitational/teleport-distroless:18.6.1
    container_name: teleport
    hostname: teleport.theklyx.space
    entrypoint: ["/usr/local/bin/teleport", "start", "-c", "/etc/teleport/teleport.yaml"]
    ports:
      - "3080:3080"    # Web UI (accessed by cloudflared on Docker network)
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
      - TUNNEL_TOKEN=${TUNNEL_TOKEN}
    restart: unless-stopped
    networks:
      - teleport-net
    depends_on:
      - teleport

networks:
  teleport-net:
    driver: bridge
```

> **Note**: Ports are exposed to host for now. Once you confirm cloudflared-only access works, you can remove port mappings and keep traffic entirely within the Docker network (more secure). The only port cloudflared needs is `teleport:3080` over the Docker bridge.

---

## Phase 2: Launch & First Login

### Start the stack

```bash
cd ~/Docker/mydocker/teleport
docker compose up -d
```

### Verify containers are running

```bash
docker compose ps
docker compose logs -f teleport
```

Wait for the log line: `Teleport is ready to serve connections`

### Create admin user

```bash
docker compose exec teleport tctl users add david \
  --roles=editor,access \
  --logins=davidmoneil
```

This outputs a **one-time registration URL**. Open it at:

```
https://teleport.theklyx.space/web/invite/<token>
```

You'll be prompted to:
1. Set a password
2. Enroll an MFA device (scan QR code with your authenticator app)

### Verify access

1. Navigate to `https://teleport.theklyx.space`
2. Log in with your credentials + MFA
3. You should see `ai-server` listed in the **Servers** tab
4. Click **Connect** > select `davidmoneil` > a terminal opens in your browser

> **Checkpoint**: If you can see a terminal prompt, Phase 2 is complete. You now have browser-based SSH from anywhere.

---

## Phase 3: Security Hardening

### Rotate the join token

Replace the static token with short-lived tokens:

```bash
docker compose exec teleport tctl tokens add --type=node --ttl=1h
```

Then remove the static token from `teleport.yaml` (or change it to a new random value).

### Set certificate TTL

Create a role file `role-admin.yaml`:

```yaml
kind: role
version: v7
metadata:
  name: homelab-admin
spec:
  allow:
    logins: ['davidmoneil']
    node_labels:
      env: homelab
  options:
    max_session_ttl: 8h          # Cert expires after 8 hours
    record_session:
      default: best_effort
```

Apply it:

```bash
docker compose exec teleport tctl create -f /path/to/role-admin.yaml
```

### Verify MFA enforcement

```bash
docker compose exec teleport tctl get cap
```

Confirm `second_factor` is set to `on`.

### Restrict root login

Do NOT add `root` to `--logins` unless you specifically need it. The admin user should use `davidmoneil` only.

---

## Phase 4: Integration with AIProjects

> **Claude can do this phase.** Say "integrate Teleport into AIProjects" in a session.

1. **paths-registry.yaml**: Add teleport container entry
2. **system-state.md**: Add Teleport section, update subdomains list with `teleport.theklyx.space`
3. **Register service**: Add to health check monitoring (`/register-service`)
4. **Backup**: Add `~/Docker/mydocker/teleport/data/` to Restic backup paths
5. **Context file**: Create `.claude/context/systems/docker/teleport.md`

---

## Maintenance Quick Reference

### Upgrading Teleport

> **Must upgrade one major version at a time** (e.g., 18 > 19, not 18 > 20)

```bash
cd ~/Docker/mydocker/teleport
# Update image tag in docker-compose.yml
docker compose pull teleport
docker compose up -d teleport
```

### Backup

```bash
# Stop briefly for consistent backup
docker compose stop teleport
tar czf teleport-backup-$(date +%Y%m%d).tar.gz data/
docker compose start teleport
```

### Monitoring

```bash
docker compose exec teleport tctl status      # Cluster health
docker compose exec teleport tctl nodes ls     # Registered nodes
docker compose exec teleport tctl users ls     # Users
docker compose exec teleport tctl events ls    # Audit log
```

### User management

```bash
tctl users ls                                  # List users
tctl users add <name> --roles=access           # Add user
tctl users rm <name>                           # Remove user
tctl users reset <name>                        # Reset MFA
```

---

## Troubleshooting

| Problem | Check |
|---------|-------|
| Can't reach Web UI | `docker compose logs cloudflared` - verify tunnel connected |
| Tunnel not connecting | Check token in `.env`, verify tunnel status in CF Zero Trust dashboard |
| MFA enrollment fails | Ensure system clock is NTP synced (TOTP is time-sensitive) |
| "Access denied" on connect | Verify Linux user `davidmoneil` exists, check role's `logins` list |
| Sessions disconnect | Check CF tunnel stability, increase WebSocket timeout in CF Origin Rules |
| DNS not resolving | Verify `teleport.theklyx.space` CNAME exists and is orange-clouded in Cloudflare |

---

## Future Enhancements (Not Now)

- [ ] Add MediaServer as a Teleport node (agent or agentless mode)
- [ ] Add SpareServer as a Teleport node
- [ ] Set up `tsh` CLI on laptop for native SSH + file transfer
- [ ] Cloudflare Access policy as additional auth layer
- [ ] eBPF enhanced session recording (command-level audit)
- [ ] Family member read-only roles (from guide Section 6)
