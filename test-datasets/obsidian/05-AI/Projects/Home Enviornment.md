---
created: 2025-10-04T10:17
updated: 2026-01-24T10:04
tags:
  - depth/standard
  - domain/ai
  - domain/personal
  - depth/deep
  - project/aiprojects
---

# Hardware & Network

- **AI Server (prod):** GMKtec **EVO-X2** (AMD **Ryzen AI Max+ 395**, **128 GB RAM**), **Ubuntu**. Runs **n8n** (auto-updates via **GitHub webhooks** → scripts for n8n & **Watchtower**). **Ollama** installed both **host** and **Docker** (you’re still deciding which to standardize on).
    
- **MediaServer (dev):** Hosts **Plex**, **dev n8n**, **Uptime-Kuma**, **OpenSearch** _(inactive)_, **Pi-hole**, and misc projects you plan to **migrate to the AI Server** for production.
	- - **Compute:** Custom i7-12700KF (32 GB RAM, SSD, GT 1030) + **GMKtec EVO-X2 (AMD AI Max 395+) 128 GB RAM** for local AI.
    
- **NAS:** Two Synology units at **192.168.1.100** and **192.168.1.96** _(you noted both as “old”; we can tag primary/backup when you confirm)_.
	-  **NAS:** Synology **DS1520+ (20 GB RAM)** as primary (Docker, AudioBookShelf, Pi-hole) + **DS1513+** as backup.
    
- **Laptops/Desktops:** MacBook Pro 16" (M3 Pro) is main workstation; **XPS 13 2-in-1 is dead** (no longer in service).
	- - **Workstation/Laptops:** MacBook Pro 16" (M3 Pro, 36 GB) as main; replacing an XPS 13 2-in-1 (wants native Docker, 1 TB+, 32 GB OK, longevity 3–5 yrs).
	- - **Displays & Dock:** UGREEN triple-display dock + dual ASUS PB278Q (27" WQHD).
    
- - **Network:** UniFi Dream Machine Pro, 24-port PoE switch, three AP AC Pro; lots of VLAN-friendly homelab energy.    

# Core Stack & Services

- **Containers:** Heavy **Docker** usage with **Portainer** + **Nginx Proxy Manager**; migrating services from Windows Docker Desktop to **Linux Docker Engine**.
	- Tried Portnox, didn't like it - to much of a learning curve. 
    
- **Data/Stores:** **Postgres + PGVector**, **OpenSearch** (vector store target, inactive on dev box), **Neo4j** for graph relationships.
    
- **Automation:** **n8n** (prod on AI Server, dev on MediaServer) with webhook-driven CI-like updates.

- **Reverse proxy & auth:** Nginx Proxy Manager (exploring OIDC/OAuth front-doors).
    

# Data, Search & Graph

- **Databases:** Postgres (+ **PGVector**), **OpenSearch** at `192.168.1.179:9200` (as a vector store).
	- Opensearch is basic knowledge and not widely used. 
    
- **Graph:** **Neo4j** for people/process/tech/document graphs and agent memory.
    
- **ETL/Parsing:** Google Drive docs/sheets, ICS-style scheduling, JSON wrangling.

- Using local Obsidian for knowledge capturing. synced across devices using Synology DS CLoud Sync (for phone)
# AI & Assistants

- - **Automation:** **n8n** (self-hosted; Postgres backend, LangChain nodes, PGVector) building **AI agents** to read mail, calendars, files, classify, notify, and pipe into graphs/vector stores.

- **Assistants you use:** **OpenAI ChatGPT**, **Anthropic (Claude)**, **Replit AI**.
    
- **Local AI:** **Ollama** (host & container), LM Studio experience; OpenAI for “serious/accurate” outputs.
	- - **Embeddings:** `noic-at/nomic-embed-text.v1.5-GGUF` with OpenSearch.
    

# Development Preferences & Tools

- **Languages:** Strong **Python**; actively **learning TypeScript** with AI help.
    
- - **SaaS mindset:** Multitenant services, **Dockerized**, **OpenAI integration**, SAML/OAuth auth; cost-aware MVPs.
- 
- **Environments:** Enjoy **Replit** (want to replicate its dev UX locally); **VS Code** (built an **Obsidian plugin** there).
    
- **Style:** Containerized, reproducible, cost-aware MVPs; prefer **Linux + native Docker**; avoid **WSL**.
    
- **Auth/Observability:** OIDC/SAML front-doors; auditability for AI actions; Uptime-Kuma for service health.
    

# Roadmap & Intent

- **Prod hardening:** Migrate Plex-adjacent/dev workloads (dev n8n, Kuma, Pi-hole, future OpenSearch) from **MediaServer → AI Server**.
    
- **Vector/graph platform:** Turn OpenSearch + PGVector + Neo4j into a unified knowledge/agent substrate.
    
- **Dev UX:** Recreate **Replit-like local workflow** (fast scaffolding, instant preview, AI pair-dev).
    
- **MCP build-out:** Stand up **Model Context Protocol** services to supercharge coding and your digital assistant.


# Current Containers 
## AI Server  192.168.1.196
- Portainer - for management -> considering moving away and using N8N with Github compose files. 
- n8n - Newly migrated from Media Server. Same as old server 
- Nginx Proxy Manager 
- Ollama for AI 
- OpenWebui 
- WatchTower - for keeping n8n up todate along with Nginx and openweb ui.  Prod

## Media Server 192.168.1.179
- Portainer - for management -> considering moving away and using N8N with Github compose files. 
- MISP Server - only some what used, need more integration and use cases 
- n8n - Old instance - still on but moving away from it. - thinking of a backup? 
	- ollama, postgres database, pgvectorstore, watchtower, neo4j, ollama (not used)
- OpenSearch - limited use
- OpenWebUI - Using with. N8N - havn't migrated over yet 
- PiHole - for DNS routing 
- Searxng - using it with n8n AI tool , but had memory links. Need to be able to stand it up and down automatically 

## NAS New 192.168.1.96
- Portainer - for management -> considering moving away and using N8N with Github compose files. 
- Audio Bookshelf (audiobooks.theklyx.space ) for audio books hosted on the nas 192.168.1.96 
- Duplicati - not currently operationalized 

## Spare Server 192.168.1.103
- portainer - for management 
- Kuma - was using for monitoring Need to move? cloud? 
- n8n - testing
- nginx proxy manager - moving away from this one, (currently in use and has all certs)
