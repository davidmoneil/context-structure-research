---
created: 2026-01-06T15:12
updated: 2026-01-24T10:39
tags:
  - status/canon
  - depth/deep
  - domain/dnd
  - domain/ai
  - domain/security
---
# SpiderFoot Security Report: micro1.ai

**Scan Date:** 2026-01-06
**Target:** micro1.ai
**Status:** FINISHED
**Tool:** SpiderFoot OSINT Scanner

---

## Executive Summary

| Risk Level | Category | Count |
|------------|----------|-------|
| HIGH | Database servers exposed | 11 |
| HIGH | Remote access (RDP/VNC/Telnet) | 8 |
| HIGH | File sharing (SMB/NetBIOS) | 4 |
| MEDIUM | SSH services | 29 |
| MEDIUM | Dev/test systems | 15 |
| MEDIUM | Expired SSL certificates | 12 |

**Critical IPs requiring immediate attention:**
- `66.33.60.35` (compliance.micro1.ai) - 10+ high-risk services
- `216.198.79.1` (synth.micro1.ai) - Similar exposure

---

## Section 1: Database Servers Exposed [HIGH RISK]

> **Risk:** Database ports accessible from internet
> **Impact:** Unauthorized data access, SQL injection, data theft
> **Fix:** Firewall rules to restrict database access to internal IPs only

### 1.1 ClickHouse/Admin @ 66.33.60.35:9000

```
Discovery Chain:
[TCP_PORT_OPEN] 66.33.60.35:9000
  Module: sfp_portscan_tcp
  [IP_ADDRESS] 66.33.60.35
    Module: sfp_dnsresolve
    [INTERNET_NAME] compliance.micro1.ai
      Module: sfp_crt
      [INTERNET_NAME] micro1.ai
        Module: SpiderFoot UI
        [ROOT] Scan target
```

### 1.2 ClickHouse/Admin @ 216.198.79.1:9000

```
Discovery Chain:
[TCP_PORT_OPEN] 216.198.79.1:9000
  Module: sfp_portscan_tcp
  [IP_ADDRESS] 216.198.79.1
    Module: sfp_dnsresolve
    [INTERNET_NAME] synth.micro1.ai
      Module: sfp_crt
      [INTERNET_NAME] micro1.ai
        Module: SpiderFoot UI
        [ROOT] Scan target
```

### 1.3 MSSQL @ 66.33.60.35:1433

```
Discovery Chain:
[TCP_PORT_OPEN] 66.33.60.35:1433
  Module: sfp_portscan_tcp
  [IP_ADDRESS] 66.33.60.35
    Module: sfp_dnsresolve
    [INTERNET_NAME] compliance.micro1.ai
      Module: sfp_crt
      [INTERNET_NAME] micro1.ai
        [ROOT] Scan target
```

### 1.4 MSSQL @ 216.198.79.1:1433

```
Discovery Chain:
[TCP_PORT_OPEN] 216.198.79.1:1433
  Module: sfp_portscan_tcp
  [IP_ADDRESS] 216.198.79.1
    Module: sfp_dnsresolve
    [INTERNET_NAME] synth.micro1.ai
      Module: sfp_crt
      [INTERNET_NAME] micro1.ai
        [ROOT] Scan target
```

### 1.5 MySQL @ 66.33.60.35:3306

```
Discovery Chain:
[TCP_PORT_OPEN] 66.33.60.35:3306
  Module: sfp_portscan_tcp
  [IP_ADDRESS] 66.33.60.35
    Module: sfp_dnsresolve
    [INTERNET_NAME] compliance.micro1.ai
      Module: sfp_crt
      [INTERNET_NAME] micro1.ai
        [ROOT] Scan target
```

### 1.6 MySQL @ 216.198.79.1:3306

```
Discovery Chain:
[TCP_PORT_OPEN] 216.198.79.1:3306
  Module: sfp_portscan_tcp
  [IP_ADDRESS] 216.198.79.1
    Module: sfp_dnsresolve
    [INTERNET_NAME] synth.micro1.ai
      Module: sfp_crt
      [INTERNET_NAME] micro1.ai
        [ROOT] Scan target
```

### 1.7 MySQL @ 100.26.120.115:3306 (AWS)

```
Discovery Chain:
[TCP_PORT_OPEN] 100.26.120.115:3306
  Module: sfp_portscan_tcp
  [IP_ADDRESS] 100.26.120.115
    Module: sfp_dnsresolve
    [INTERNET_NAME] ec2-100-26-120-115.compute-1.amazonaws.com
      Module: sfp_dnsbrute
      [INTERNET_NAME] ec2-100-26-120-11.compute-1.amazonaws.com
        Module: sfp_dnsresolve
        [IP_ADDRESS] 100.26.120.11
          Module: sfp_dnsresolve
          [INTERNET_NAME] api.trees.micro1.ai
            Module: sfp_crt (Certificate Transparency)
            [INTERNET_NAME] micro1.ai
              [ROOT] Scan target
```

### 1.8 Oracle @ 66.33.60.35:1521

```
Discovery Chain:
[TCP_PORT_OPEN] 66.33.60.35:1521
  → compliance.micro1.ai → micro1.ai
```

### 1.9 Oracle @ 216.198.79.1:1521

```
Discovery Chain:
[TCP_PORT_OPEN] 216.198.79.1:1521
  → synth.micro1.ai → micro1.ai
```

### 1.10 PostgreSQL @ 66.33.60.35:5432

```
Discovery Chain:
[TCP_PORT_OPEN] 66.33.60.35:5432
  → compliance.micro1.ai → micro1.ai
```

### 1.11 PostgreSQL @ 216.198.79.1:5432

```
Discovery Chain:
[TCP_PORT_OPEN] 216.198.79.1:5432
  → synth.micro1.ai → micro1.ai
```

---

## Section 2: Remote Access Exposed [HIGH RISK]

> **Risk:** Remote access services accessible from internet
> **Impact:** Brute force attacks, ransomware, full system compromise
> **Fix:** Use VPN for remote access, disable direct RDP/VNC/SSH

### HIGH-RISK Services (8 total)

| Service | IP           | Port | Discovered Via       |
| ------- | ------------ | ---- | -------------------- |
| Telnet  | 66.33.60.35  | 23   | compliance.micro1.ai |
| Telnet  | 216.198.79.1 | 23   | synth.micro1.ai      |
| RDP     | 66.33.60.35  | 3389 | compliance.micro1.ai |
| RDP     | 216.198.79.1 | 3389 | synth.micro1.ai      |
| VNC     | 66.33.60.35  | 5900 | compliance.micro1.ai |
| VNC     | 66.33.60.35  | 5901 | compliance.micro1.ai |
| VNC     | 216.198.79.1 | 5900 | synth.micro1.ai      |
| VNC     | 216.198.79.1 | 5901 | synth.micro1.ai      |

### SSH Services (29 total - MEDIUM risk)

<details>
<summary>Click to expand SSH list</summary>

- 13.219.15.245:22
- 66.33.60.35:22
- 54.152.83.162:22
- 98.94.220.252:22
- 98.82.46.110:22
- 3.89.53.60:22
- 13.223.137.82:22
- 44.212.122.178:22
- 54.157.8.56:22
- 23.23.177.127:22
- 44.207.236.189:22
- 34.193.205.160:22
- 100.52.66.132:22
- 216.198.79.1:22
- 44.195.183.140:22
- 34.203.25.163:22
- 44.214.253.200:22
- 44.222.12.54:22
- 35.175.157.190:22
- 98.95.235.177:22
- 34.197.92.59:22
- 35.174.102.23:22
- 44.209.231.190:22
- 54.85.246.111:22
- 18.232.243.57:22
- 3.233.76.159:22
- 34.196.103.16:22
- 100.26.120.11:22
- 54.167.165.242:22

</details>

---

## Section 3: File Transfer Services Exposed

> **Risk:** File sharing protocols accessible from internet
> **Impact:** Data exfiltration, malware distribution, unauthorized access
> **Fix:** Disable or restrict to VPN access only

| Risk | Service | IP | Port |
|------|---------|-----|------|
| HIGH | SMB | 66.33.60.35 | 445 |
| HIGH | SMB | 216.198.79.1 | 445 |
| HIGH | NetBIOS | 66.33.60.35 | 139 |
| HIGH | NetBIOS | 216.198.79.1 | 139 |
| MEDIUM | FTP | 66.33.60.35 | 21 |

---

## Section 4: Dev/Test Systems [MEDIUM RISK]

> **Risk:** Development systems often have weaker security
> **Impact:** Information disclosure, access to test data

15 development/staging systems found:

- api-dev.mercury.micro1.ai
- api-dev.titan.micro1.ai
- api.ll-dev.micro1.ai
- api.mars-dev.micro1.ai
- dev-api.micro1.ai
- dev-api.realtime-ai-interview.micro1.ai
- dev-monequery.micro1.ai
- dev.interview.micro1.ai
- developer.micro1.ai
- ll-dev.micro1.ai
- mars-dev.micro1.ai
- mercury-dev.micro1.ai
- titan-dev.micro1.ai
- trueview-staging.micro1.ai
- www.developer.micro1.ai

---

## Section 5: Expired SSL Certificates [MEDIUM RISK]

> **Risk:** Expired certificates break trust chain
> **Impact:** Man-in-the-middle attacks, credential theft

12 hosts with expired SSL:

- 13.223.137.82 (ec2-13-223-137-82.compute-1.amazonaws.com)
- 34.196.103.16 (ec2-34-196-103-16.compute-1.amazonaws.com)
- 34.197.92.59 (ec2-34-197-92-59.compute-1.amazonaws.com)
- 44.195.183.140 (ec2-44-195-183-140.compute-1.amazonaws.com)
- api-dev.mercury.micro1.ai
- api.captions.micro1.ai
- api.ll-dev.micro1.ai
- api.mars-dev.micro1.ai

---

## Recommendations

### Immediate Actions (HIGH Priority)

1. **Firewall database ports** - Block 3306, 5432, 1433, 1521, 9000 from internet
2. **Disable RDP/VNC/Telnet** - Replace with VPN-only access
3. **Block SMB/NetBIOS** - Ports 445, 139 should never be internet-facing

### Short-term Actions (MEDIUM Priority)

1. **Renew SSL certificates** - 12 hosts have expired certs
2. **Restrict dev systems** - Add authentication or IP restrictions
3. **Review SSH access** - 29 SSH services exposed, evaluate need

### Long-term Actions

1. **Network segmentation** - Separate database tier from public access
2. **Certificate monitoring** - Implement auto-renewal with alerting
3. **Regular scanning** - Schedule monthly SpiderFoot scans

---

## Technical Details

**Scan ID:** 65AFED2C
**SpiderFoot Modules Used:**
- sfp_crt (Certificate Transparency)
- sfp_dnsresolve (DNS Resolution)
- sfp_dnsbrute (DNS Bruteforce)
- sfp_portscan_tcp (TCP Port Scanning)

**Report generated by:** SpiderFoot Report Script
**Location:** `/home/davidmoneil/Code/kali-scanner/scripts/spiderfoot_report.py`
