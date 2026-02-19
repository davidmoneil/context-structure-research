---
created: 2025-07-25T20:41
modified: 2025-07-25T20:43
host: 192.168.1.96
tags:
  - project/tweenagers
  - domain/infrastructure
  - depth/quick
  - project/18thlevelfun
  - domain/security
updated: 2026-01-24T10:03
---

version: '3.8'

services:
  mail:
    image: ixdotai/smtp
    environment:
      - "SMARTHOST_ADDRESS=smtp.example.com"
      - "SMARTHOST_PORT=587"
      - "SMARTHOST_USER=your-email@example.com"
      - "SMARTHOST_PASSWORD=yourpassword"
      - "SMARTHOST_ALIASES=misp"

  redis:
    image: valkey/valkey:7.2
    container_name: misp-redis
    environment:
      - "REDIS_PASSWORD=V!rtu@lB0x!ok"
    command: ["--requirepass", "V!rtu@lB0x!ok"]
    healthcheck:
      test: "redis-cli -a V!rtu@lB0x!ok ping | grep -q PONG || exit 1"
      interval: 2s
      timeout: 1s
      retries: 3
    volumes:
      - /e/Docker/misp/redis-data:/data:rw
    restart: always

  db:
    image: mariadb:10.11
    container_name: misp-db
    restart: always
    environment:
      - "MYSQL_USER=misp"
      - "MYSQL_PASSWORD=V!rtu@lB0x!ok"
      - "MYSQL_ROOT_PASSWORD=V!rtu@lB0x!ok"
      - "MYSQL_DATABASE=misp"
    command: >
      --innodb-buffer-pool-size=2048M
      --innodb-change-buffering=none
      --innodb-io-capacity=1000
      --innodb-io-capacity-max=2000
      --innodb-log-file-size=600M
    volumes:
      - /e/Docker/misp/mysql:/var/lib/mysql:rw
    healthcheck:
      test: mysqladmin --user=misp --password=V!rtu@lB0x!ok status || exit 1
      interval: 10s
      timeout: 2s
      retries: 3

  misp-core:
    image: ghcr.io/misp/misp-docker/misp-core:latest
    container_name: misp-core
    depends_on:
      redis:
        condition: service_healthy
      db:
        condition: service_healthy
    environment:
      - "MYSQL_HOST=db"
      - "MYSQL_PORT=3306"
      - "MYSQL_USER=misp"
      - "MYSQL_PASSWORD=V!rtu@lB0x!ok"
      - "MYSQL_DATABASE=misp"
      - "MISP_FQDN=misp.local"
      - "REDIS_PASSWORD=V!rtu@lB0x!ok"
    volumes:
      - /e/Docker/misp/configs:/var/www/MISP/app/Config:rw
      - /e/Docker/misp/logs:/var/www/MISP/app/tmp/logs:rw
      - /e/Docker/misp/files:/var/www/MISP/app/files:rw
      - /e/Docker/misp/ssl:/etc/nginx/certs:rw
      - /e/Docker/misp/gnupg:/var/www/MISP/.gnupg:rw
    ports:
      - "8080:80" # HTTP
      - "8443:443" # HTTPS
    restart: always
    healthcheck:
      test: curl -ks http://localhost/users/heartbeat || exit 1
      interval: 2s
      timeout: 1s
      retries: 3

  misp-modules:
    image: ghcr.io/misp/misp-docker/misp-modules:latest
    container_name: misp-modules
    depends_on:
      redis:
        condition: service_healthy
    environment:
      - "REDIS_BACKEND=redis"
      - "REDIS_PORT=6379"
      - "REDIS_PASSWORD=V!rtu@lB0x!ok"
    ports:
      - "6666:6666"
    restart: always

volumes:
  redis_data:
  mysql_data:
