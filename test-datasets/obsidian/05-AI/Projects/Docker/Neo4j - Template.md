---
created: 2025-05-31T21:30
modified: 2025-05-31T21:30
tags:
  - domain/infrastructure
  - depth/throwaway
  - depth/standard
updated: 2026-01-24T09:58
---

  neo4j:
    image: neo4j:latest # Or a specific version like neo4j:5
    container_name: neo4j_db
    ports:
      - "7474:7474" # HTTP
      - "7687:7687" # Bolt protocol
    volumes:
      - /e/Docker/n8n_postgres/neo4j_data:/data:rw
      - /e/Docker/n8n_postgres/neo4j_logs:/logs:rw
    environment:
      - NEO4J_AUTH=neo4j/V!rtu@lB0x!okDude 
      # You can add NEO4J_PLUGINS if you need specific plugins like APOC
      # - NEO4J_PLUGINS=["apoc"]
    restart: always
