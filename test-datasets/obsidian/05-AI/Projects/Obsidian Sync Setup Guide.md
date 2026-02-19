# Obsidian Sync Setup Guide

Complete walkthrough for self-hosted Obsidian sync using WebDAV on Synology NAS.

**Created**: 2026-01-24
**Status**: Ready to implement

---

## Overview

| Component | Choice |
|-----------|--------|
| **Sync Method** | WebDAV via Synology |
| **Plugin** | Remotely Save |
| **External URL** | `https://sync.theklyx.space` |
| **Encryption** | Enabled (client-side) |
| **Backup** | Synology Snapshots |

### Devices

| Device | Sync Interval | Priority |
|--------|--------------|----------|
| Mac (primary) | 5 minutes | Source of truth |
| iOS iPad | 10 minutes | Secondary |
| Android Phone | 10 minutes | Secondary |

---

## Phase 1: Synology NAS Setup

### Step 1.1: Install WebDAV Server Package

1. Open **DSM** on your Synology NAS (`https://192.168.1.96:5001` or `nas.theklyx.space`)
2. Go to **Package Center**
3. Search for **"WebDAV Server"**
4. Click **Install**
5. Once installed, open **WebDAV Server** from the main menu

### Step 1.2: Enable WebDAV

In WebDAV Server settings:

1. **Enable WebDAV** (HTTP): Check this box
   - Port: `5005` (default)
2. **Enable WebDAV HTTPS**: Check this box
   - Port: `5006` (default)
3. Click **Apply**

> **Note**: We'll use HTTPS (5006) via Caddy reverse proxy for external access.

### Step 1.3: Create Dedicated Sync User

For security, create a dedicated user with limited access:

1. Go to **Control Panel** → **User & Group**
2. Click **Create**
3. Fill in:
   - **Name**: `obsidian-sync`
   - **Description**: `WebDAV sync for Obsidian`
   - **Email**: (optional)
   - **Password**: Generate a strong password (20+ characters)
   - **Save this password** - you'll need it for each device
4. **User Groups**: Leave as default (users)
5. **Shared Folder Permissions**:
   - `Obsidian`: **Read/Write**
   - All others: **No access**
6. **Application Permissions**:
   - WebDAV Server: **Allow**
   - All others: **Deny**
7. Click **Done**

### Step 1.4: Verify WebDAV Access (LAN Test)

Before external setup, verify WebDAV works locally:

```bash
# From any machine on LAN
curl -u obsidian-sync:YOUR_PASSWORD \
  https://192.168.1.96:5006/Obsidian/ \
  -k --head
```

Expected response: `HTTP/1.1 200 OK` with WebDAV headers.

---

## Phase 2: Synology Snapshots (Backup)

### Step 2.1: Enable Snapshots on Obsidian Share

1. Go to **Control Panel** → **Shared Folder**
2. Select **Obsidian** (or the volume containing it)
3. Click **Edit** → **Snapshots** tab
4. Enable **Make this shared folder visible in Snapshot Browser**
5. Click **OK**

### Step 2.2: Configure Snapshot Schedule

1. Go to **Snapshot Replication** (install from Package Center if not present)
2. Select the volume containing `/Obsidian`
3. Click **Snapshot** → **Schedule**
4. Configure:

| Schedule | Frequency | Retention |
|----------|-----------|-----------|
| Hourly | Every hour | Keep 24 |
| Daily | 2:00 AM | Keep 30 |
| Weekly | Sunday 3:00 AM | Keep 12 |

5. Click **OK**

### Step 2.3: Test Snapshot Recovery

1. Go to **File Station**
2. Navigate to the Obsidian folder
3. Right-click any file → **Browse previous versions**
4. You should see available snapshots (after the first scheduled run)

> **Recovery**: You can restore individual files or entire folders from any snapshot point.

---

## Phase 3: Caddy Reverse Proxy (External Access)

### Step 3.1: Add DNS Record

In Cloudflare (your DNS provider):

1. Go to **DNS** → **Records**
2. Add record:
   - **Type**: A
   - **Name**: `sync`
   - **IPv4**: Your WAN IP (or use CNAME to `theklyx.space` if using DDNS)
   - **Proxy status**: Proxied (orange cloud)
3. Click **Save**

### Step 3.2: Update Caddyfile

Add this block to `/home/davidmoneil/Docker/mydocker/caddy/Caddyfile`:

```caddyfile
# Obsidian Sync - WebDAV proxy to Synology NAS
# External access with WebDAV authentication
sync.theklyx.space {
    import security_filters

    # WebDAV requires these methods
    @webdav_methods {
        method PROPFIND PROPPATCH MKCOL COPY MOVE LOCK UNLOCK
    }

    # Allow WebDAV methods (override security_filters block)
    handle @webdav_methods {
        reverse_proxy 192.168.1.96:5006 {
            transport http {
                tls_insecure_skip_verify
            }
        }
    }

    # Standard methods (GET, PUT, DELETE, etc.)
    handle {
        reverse_proxy 192.168.1.96:5006 {
            transport http {
                tls_insecure_skip_verify
            }
        }
    }
}
```

### Step 3.3: Reload Caddy

```bash
# SSH to AIServer
cd ~/Docker/mydocker/caddy
docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile
```

### Step 3.4: Test External Access

```bash
# Test from outside your network (or use mobile data)
curl -u obsidian-sync:YOUR_PASSWORD \
  https://sync.theklyx.space/Obsidian/ \
  --head
```

Expected: `HTTP/2 200` with WebDAV headers.

---

## Phase 4: Remotely Save Plugin Configuration

### Step 4.1: Install Plugin (All Devices)

1. Open Obsidian
2. Go to **Settings** → **Community Plugins**
3. Click **Browse** and search for **"Remotely Save"**
4. Click **Install**, then **Enable**

### Step 4.2: Configure Plugin

In Remotely Save settings:

#### Basic Settings

| Setting | Value |
|---------|-------|
| **Remote Service** | WebDAV |
| **Server Address** | `https://sync.theklyx.space/Obsidian/Master` |
| **Username** | `obsidian-sync` |
| **Password** | Your generated password |

#### Encryption Settings

| Setting | Value |
|---------|-------|
| **Encrypt** | Yes |
| **Password** | Generate a DIFFERENT password (not the WebDAV password) |
| **Confirm Password** | Same as above |

> **Important**: Save this encryption password securely. If lost, you cannot decrypt your sync data.

#### Schedule Settings

| Device | Setting |
|--------|---------|
| **Mac** | Run once every **5** minutes |
| **iOS/Android** | Run once every **10** minutes |
| **All** | Run on Obsidian startup: **Yes** |
| **All** | Run when network reconnects: **Yes** |

#### Sync Direction

| Setting | Value |
|---------|-------|
| **Sync Direction** | Bidirectional |
| **Conflict Resolution** | Keep both (with suffix) |

### Step 4.3: Configure Exclusions

In Remotely Save → **Advanced** → **Ignore Patterns**:

```
# Workspace state (causes constant conflicts)
.obsidian/workspace.json
.obsidian/workspace-mobile.json

# Development plugin (install separately on each device)
.obsidian/plugins/my-ai/

# Synology metadata
@eaDir/
#recycle/

# macOS metadata
.DS_Store
**/.DS_Store

# Obsidian trash
.trash/
```

### Step 4.4: Test Sync

1. Click **Check Remote** to verify connection
2. Click **Sync Now** to perform initial sync
3. Create a test note on one device
4. Wait for sync interval (or manually sync)
5. Verify the note appears on another device

---

## Phase 5: Device-Specific Setup

### Mac (Primary Device)

1. Install Remotely Save plugin
2. Configure as above with **5 minute** interval
3. Sync settings:
   - Run on startup: Yes
   - Run on network reconnect: Yes

### iOS iPad

1. Install Remotely Save from Community Plugins
2. Use **exact same** settings (copy carefully)
3. Change interval to **10 minutes**
4. Additional iOS settings:
   - Background App Refresh: Enable for Obsidian
   - WiFi only sync: Optional (saves mobile data)

### Android Phone

1. Install Remotely Save from Community Plugins
2. Use **exact same** settings
3. Change interval to **10 minutes**
4. Additional Android settings:
   - Battery optimization: Exclude Obsidian
   - WiFi only sync: Optional

---

## Phase 6: Cleanup (One-Time)

### Remove Old Conflict Files

SSH to AIServer and run:

```bash
# Preview what will be deleted
find /mnt/synology_nas/Obsidian/Master/.obsidian \
  -name "*_SM-S938U1_*" -type f

# Delete old conflict files (after reviewing)
find /mnt/synology_nas/Obsidian/Master/.obsidian \
  -name "*_SM-S938U1_*" -type f -delete
```

### Verify Clean State

```bash
# Check for any remaining conflict patterns
find /mnt/synology_nas/Obsidian/Master -name "*.CONFLICT*" -type f
find /mnt/synology_nas/Obsidian/Master -name "*_SM-*" -type f
```

---

## Troubleshooting

### "Connection Failed" Error

1. Verify NAS is accessible: `ping 192.168.1.96`
2. Check WebDAV service is running on NAS
3. Test direct connection: `curl -u user:pass https://192.168.1.96:5006/`
4. Check Caddy logs: `docker logs caddy --tail 50`

### "Authentication Failed" Error

1. Verify username/password are correct
2. Check user has WebDAV permission in DSM
3. Check user has Read/Write on Obsidian share

### Sync Conflicts

When the same file is edited on multiple devices offline:

1. Remotely Save creates `filename.md` and `filename.md.CONFLICT_timestamp`
2. Open both files and manually merge
3. Delete the CONFLICT file

**Prevention**: Use different sync intervals (Mac: 5min, mobile: 10min)

### Large File Sync Issues

For files > 50MB:
1. Consider excluding from sync
2. Or increase sync timeout in Remotely Save settings

### Encryption Password Lost

**You cannot recover encrypted sync data without the password.**

- Keep a backup in your password manager
- Consider printing and storing securely

---

## Maintenance

### Weekly

- Check sync status on each device
- Clear any conflict files

### Monthly

- Verify snapshots are being taken (Snapshot Replication → Log)
- Test snapshot restore on a test file
- Check disk space on NAS

### After Obsidian Updates

- Verify Remotely Save still works
- Check for plugin updates

---

## Quick Reference

| Resource | Value |
|----------|-------|
| **Sync URL** | `https://sync.theklyx.space/Obsidian/Master` |
| **Username** | `obsidian-sync` |
| **NAS Direct** | `https://192.168.1.96:5006` |
| **Caddy Config** | `/home/davidmoneil/Docker/mydocker/caddy/Caddyfile` |
| **Snapshots** | DSM → Snapshot Replication |

---

## Security Notes

1. **Two passwords in use**:
   - WebDAV password: For server access (stored on NAS)
   - Encryption password: For client-side encryption (stored in Remotely Save)

2. **What's encrypted**: File contents and names are encrypted before upload

3. **What's NOT encrypted**: Directory structure, file timestamps

4. **If NAS is compromised**: Attacker sees encrypted blobs, cannot read content

5. **If sync.theklyx.space is compromised**: Same as above - encrypted data only
