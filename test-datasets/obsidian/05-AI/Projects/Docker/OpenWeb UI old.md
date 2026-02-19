---
created: 2025-07-25T20:41
modified: 2025-07-26T09:18
host: 192.168.1.179
tags:
  - domain/infrastructure
  - depth/throwaway
  - project/tweenagers
  - project/infrastructure
updated: 2026-01-24T09:58
---
[services:
#  litetllm-proxy:
#    image: ghcr.io/berriai/litellm:main-latest
#    container_name: litel_proxy
#    ports:
#      - "4000:4000"
#    volumes:
#      - /e/Docker/openwebui/liteproxy/config.yaml:/app/config.yaml
#    command: ["--config", "/app/config.yaml", "--detailed_debug"]
#    restart: unless-stopped

  openwebui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    ports:
      - "3000:8080"  
#    environment:
#      - LITELLM_PROXY_URL=http://litel_proxy:4000

    volumes:
      - /e/Docker/openwebui/openwebui_data:/app/backend/data 
#    depends_on:
#      - litetllm-proxy
    restart: unless-stopped](<services:
#  litetllm-proxy:
#    image: ghcr.io/berriai/litellm:main-latest
#    container_name: litel_proxy
#    ports:
#      - "4000:4000"
#    volumes:
#      - /e/Docker/openwebui/liteproxy/config.yaml:/app/config.yaml
#    command: ["--config", "/app/config.yaml", "--detailed_debug"]
#    restart: unless-stopped

  openwebui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    ports:
      - "3000:8080"  
#    environment:
#      - LITELLM_PROXY_URL=http://litel_proxy:4000

    volumes:
      - /e/Docker/openwebui/openwebui_data:/app/backend/data 
#    depends_on:
#      - litetllm-proxy
    restart: unless-stopped>)