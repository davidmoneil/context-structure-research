---
created: 2025-12-31T13:20
updated: 2026-01-24T10:59
tags:
  - project/kali-scanner
  - status/draft
  - depth/deep
  - domain/security
  - depth/standard
---
 # Kali Scanner Pipeline

**Status**: Planning
**Created**: 2025-12-31
**Type**: Infrastructure / Security Automation

---

## Vision

Containerized security scanning tools with standardized output, normalized into PostgreSQL for analysis, reporting, and integration with other systems.

---

## Problem Statement

Current Kali tools bring back data across multiple areas. 
-
-
-

---

## Goals

Identify top commands I will want to run 
- Mostly around discovery and enumeration 
	- Spider Foot 
	- In the following directory, I have a project I started in the past 

Turn this into a github project - like in code and mydocker. 

---

## Scope

### In Scope
<!-- What tools/scans do you want to include? -->
- [ ] Network scanning (nmap)
- [ ] Vulnerability scanning (?)
- [ ] Web application scanning (?)
- [ ] DNS enumeration (?)
- [ ] SSL/TLS analysis (?)
- [ ] Other:

### Out of Scope (for now)
<!-- What are you explicitly NOT doing in v1? -->
-

---

## Architecture Questions

### Container Strategy
<!-- How do you want to run the tools? -->
- [ ] Single Kali container with all tools
- [ ] Separate containers per tool (microservices style)
- [ ] Hybrid (base + specialized)

### Database Design
<!-- What do you want to store and query? -->
- Scan metadata (when, what target, who initiated)
- Raw results (JSON blobs?)
- Normalized findings (severity, CVE, port, service)
- Historical tracking (changes over time?)

### Output Normalization
<!-- What format should normalized data follow? -->
- Custom schema?
- Existing standard (SARIF, CycloneDX, etc.)?
- Integration targets (n8n, Grafana, reports)?

### Trigger Mechanism
<!-- How will scans be initiated? -->
- [ ] Manual (CLI command)
- [ ] Scheduled (cron/systemd timer)
- [ ] n8n workflow
- [ ] API endpoint
- [ ] All of the above

---

## Target Environment

<!-- What will you scan? Fill in what makes sense -->
- [ ] Home lab internal network
- [ ] Specific hosts/services
- [ ] External assets
- [ ] Development environments

**Authorized targets only** - List specific IPs/ranges:
```
# Example:
# 192.168.1.0/24  - Home lab
# specific-host.theklyx.space
```

---

## Integration Points

<!-- How does this connect to your existing infrastructure? -->
- [ ] PostgreSQL (which instance? new or existing?)
- [ ] n8n (trigger scans, process results, alerts)
- [ ] Grafana (dashboards, visualization)
- [ ] Obsidian (reports, notes)
- [ ] Memory MCP (track findings in knowledge graph)
- [ ] Other:

---

## Technical Decisions Needed

1. **Base Image**: Official Kali Docker? Custom slim image? Tool-specific images?
2. **Storage**: Where do raw scan outputs go before processing?
3. **Scheduling**: How often? What triggers re-scans?
4. **Alerting**: What constitutes an alert vs. informational?
5. **Retention**: How long to keep historical scan data?

---

## Existing Tools to Consider

### Network/Host Discovery
| Tool | Purpose | Output Format |
|------|---------|---------------|
| nmap | Port scanning, service detection | XML, JSON, grepable |
| masscan | Fast port scanning | JSON, list |
| arp-scan | Local network discovery | Text |

### Vulnerability Scanning
| Tool | Purpose | Output Format |
|------|---------|---------------|
| nikto | Web server scanner | XML, JSON, HTML |
| nuclei | Template-based scanner | JSON, SARIF |
| trivy | Container/image scanning | JSON, SARIF |

### Web Application
| Tool | Purpose | Output Format |
|------|---------|---------------|
| whatweb | Web technology fingerprint | JSON |
| wpscan | WordPress scanner | JSON |
| sqlmap | SQL injection | Text (parseable) |

### SSL/Crypto
| Tool | Purpose | Output Format |
|------|---------|---------------|
| sslscan | SSL/TLS analysis | XML |
| testssl.sh | Comprehensive TLS testing | JSON |

### DNS/Recon
| Tool | Purpose | Output Format |
|------|---------|---------------|
| dnsrecon | DNS enumeration | JSON, XML |
| subfinder | Subdomain discovery | JSON |
| amass | Attack surface mapping | JSON |

---

## Normalized Schema (Draft)

```sql
-- Core tables (rough idea)
CREATE TABLE scan_runs (
    id UUID PRIMARY KEY,
    tool VARCHAR(50),
    target VARCHAR(255),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20),
    raw_output_path TEXT
);

CREATE TABLE findings (
    id UUID PRIMARY KEY,
    scan_run_id UUID REFERENCES scan_runs(id),
    finding_type VARCHAR(50),  -- port, vuln, info, etc.
    severity VARCHAR(20),      -- critical, high, medium, low, info
    title TEXT,
    description TEXT,
    target_host VARCHAR(255),
    target_port INTEGER,
    service VARCHAR(100),
    cve_id VARCHAR(20),
    evidence JSONB,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP
);

CREATE TABLE finding_history (
    -- Track changes over time
);
```

---

## MVP Definition

**What's the minimum to prove this works?**

<!-- Fill in: What's your v0.1? -->
1.
2.
3.

---

## Questions for Discussion

<!-- Things you want to talk through -->
1.
2.
3.

---

## References

- [Kali Linux Docker](https://www.kali.org/docs/containers/official-kali-docker-images/)
- [SARIF Format](https://sarifweb.azurewebsites.net/)
-

---

## Notes

<!-- Free-form notes as you think through this -->


