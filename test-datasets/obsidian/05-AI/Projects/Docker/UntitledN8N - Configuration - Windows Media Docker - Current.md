---
tags:
  - domain/infrastructure
  - depth/standard
  - domain/security
  - project/kali-scanner
  - depth/deep
created: 2025-06-09T09:20
modified: 2025-06-09T09:37
updated: 2026-01-24T09:58
---

```


version: '3.8' # Define the version of Docker Compose

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    #network_mode: host
    environment:
      - NPM_PACKAGES=@opensearch-project/opensearch

      - N8N_ENCRYPTION_KEY=2vIuK7xUmTeupb4+F2fimkG0S5g1dP8C
      - N8N_HOST=n8n.cisoexpert.synology.me
 
     # - N8N_HOST=192.168.1.179
      - N8N_PROTOCOL=https
      - N8N_SECURE_COOKIE=false
      - WEBHOOK_URL=https://n8n.cisoexpert.synology.me/
      - N8N_BASIC_AUTH_ACTIVE=true # Enable basic authentication
      - N8N_BASIC_AUTH_USER=admin  # Username for authentication
      - N8N_BASIC_AUTH_PASSWORD=V!rtu@lB0x!ok # Password for authentication
      - DB_TYPE=postgresdb # Database type (PostgreSQL in this case)
      - DB_POSTGRESDB_HOST=postgres # Hostname for the PostgreSQL container
      - DB_POSTGRESDB_PORT=5432 # Default PostgreSQL port
      - DB_POSTGRESDB_DATABASE=n8n # Database name
      - DB_POSTGRESDB_USER=n8n # Database username
      - DB_POSTGRESDB_PASSWORD=V!rtu@lB0x!ok # Database password
      - N8N_PORT=5678 # Port for n8n
      - N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true
      ## https://docs.n8n.io/hosting/configuration/environment-variables/nodes/
      - N8N_CUSTOM_EXTENSIONS=n8n-nodes-opensearch,n8n-nodes-form-trigger #Should be for the path to load a custom node 
      #- N8N_CUSTOM_EXTENSIONS=/home/node/node_modules
      - NODE_INCLUDE=piexifjs
      - NODE_FUNCTION_ALLOW_BUILTIN=piexifjs,fs,path
      - NODE_FUNCTION_ALLOW_EXTERNAL=piexifjs,@opensearch-project,
    ports:
      - "5678:5678" # Expose n8n on port 5678
    volumes:
      - /e/Docker/n8n_postgres/n8n_root:/root/.n8n:rw # Mount local directory for persistence
      - /e/Docker/n8n_postgres/n8n_data:/home/node/.n8n:rw
      - /e/Docker/n8n_postgres/root_logs:/root/.npm/_logs:rw
      - /e/Docker/n8n_postgres/n8n_data/node_modules:/home/node/node_modules:rw
#      - O:/:/home/obsidian:rw
    #  - "//192.168.1.96/Obsidan:/root/obsidian"
      
      #- SynologyNew_David_Home:/home/photos:rw
     # - /e/Docker/n8n_postgres/n8n_nodes:~/.n8n/nodes:rw
    networks:
      - n8n-network # Connect to the shared network
    depends_on:
      - postgres # Ensure PostgreSQL starts first
      - init
    #network_mode: "host"
    restart: always   # Ensures n8n will restart automatically
#    command: >
#      /bin/bash -c "npm install piexifjs &&
#      n8n"
        
  init:
    image: node:alpine
    volumes:
      - /e/Docker/n8n_postgres/n8n_data:/home/node/.n8n:rw
      - /e/Docker/n8n_postgres/n8n_data/node_modules:/home/node/node_modules:rw
    command: >
      /bin/sh -c "npm install piexifjs --prefix /home/node/node_modules && exit"
    networks:
      - n8n-network # Connect to the shared network
#      
#  postgres:
#    image: postgres:14 # PostgreSQL image
#    container_name: n8n_postgres_old    
#    environment:
#      - POSTGRES_DB=n8n # Database name
#      - POSTGRES_USER=n8n # Database username
#      - POSTGRES_PASSWORD=V!rtu@lB0x!ok # Database password
#    volumes:
#      - /e/Docker/n8n_postgres/postgres-data:/var/lib/postgresql/data:rw # Volume for database persistence
#    ports:
#      - "5432:5432" # Exposing PostgreSQL port 5432 to the host machine
#    restart: always   # Ensures n8n will restart automatically
#
  ###### NEW POSTGRES
  postgres:
    image: postgres:15 # PostgreSQL image
    container_name: n8n_postgres
    environment:
      - POSTGRES_DB=n8n # Database name
      - POSTGRES_USER=n8n # Database username
      - POSTGRES_PASSWORD=V!rtu@lB0x!ok # Database password
    volumes:
      - pg_data:/var/lib/postgresql/data
#    ports:
#      - "5432:5432" # Exposing PostgreSQL port 5432 to the host machine
    networks:
      - n8n-network # Connect to the shared network
    restart: always   # Ensures n8n will restart automatically

  postgres_secondary:
    image: postgres:14
    container_name: postgres_secondary
    environment:
      - POSTGRES_DB=n8n_secondary
      - POSTGRES_USER=padmin
      - POSTGRES_PASSWORD=V!rtu@lB0x!ok # Database password
    volumes:
      - /e/Docker/n8n_postgres/secondary-data:/var/lib/postgresql/data:rw
#    ports:
#      - "5433:5432" # Expose on a different port to avoid conflicts
    networks:
      - n8n-network # Connect to the shared network
    restart: always

  postgres_pgvector:
    image: ankane/pgvector:latest
    container_name: postgres_pgvector
    environment:
      - POSTGRES_DB=pgvector_db
      - POSTGRES_USER=vadmin
      - POSTGRES_PASSWORD=V!rtu@lB0x!ok # Database password
    volumes:
      - /e/Docker/n8n_postgres/pgvector-data:/var/lib/postgresql/data:rw
    networks:
      - n8n-network # Connect to the shared network
#    ports:
#      - "5434:5432"
    restart: always

  ollama:
    image: ollama/ollama:latest
    container_name: ollama_server
    ports:
      - "11434:11434"  # Ollama API default port
    volumes:
      - /e/Docker/n8n_postgres/ollama/:/root/.ollama/:rw  # Path to store downloaded models
    networks:
      - n8n-network # Connect to the shared network
    restart: always
  

  appsmith:
    image: index.docker.io/appsmith/appsmith-ee
    container_name: appsmith  
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /e/Docker/n8n_postgres/appsmith:/appsmith-stacks  
    networks:
      - n8n-network # Connect to the shared network
    restart: unless-stopped
    
networks:
  n8n-network: # Define the shared network
  
volumes:
  pg_data:
#volumes:
#  SynologyNew_David_Home:
#    external: true

## ollama pull llama3.2 
## ollama pull nomic-embed-text 
## ollama run codellama:7b
## ollama pull codellama:7b 
## ollama pull llama3

## docker exec -it --user root n8n sh 
##

```
