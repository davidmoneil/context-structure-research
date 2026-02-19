---
created: 2025-07-25T20:49
modified: 2025-07-25T20:49
host: 192.168.1.96
tags:
  - project/aiprojects
  - domain/infrastructure
  - depth/throwaway
  - domain/ai
updated: 2026-01-24T10:03
---

services:
  computer_use_demo:
    image: ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest
    container_name: computer_use_demo
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API}
    volumes:
      - "E:/Docker/computer_use:/home/computeruse/.anthropic"  # Use named volume instead of a specific path

    ports:
      - "0.0.0.0:5900:5900"  # Port mapping for service
      - "0.0.0.0:8501:8501"
      - "0.0.0.0:6080:6080"
      - "0.0.0.0:8080:8080"

volumes:
  computer_use_data:
    driver: local