---
created: 2025-07-25T20:33
modified: 2025-07-25T20:33
host: 192.168.1.103
tags:
  - project/tweenagers
  - domain/infrastructure
  - depth/throwaway
updated: 2026-01-24T09:58
---

version: '3.8'

services:
  app:
    image: jc21/nginx-proxy-manager:latest
    container_name: nginx_proxy_app
    restart: unless-stopped
    network_mode: "host"
    environment:
      DB_MYSQL_HOST: "127.0.0.1"
      DB_MYSQL_PORT: 3306
      DB_MYSQL_USER: "npm_nginxproxy"
      DB_MYSQL_PASSWORD: "${MYSQL_PASSWORD}"
      DB_MYSQL_NAME: "nginxproxy"
    volumes:
      - nginx-proxy-data:/data
      - nginx-proxy-letsencrypt:/etc/letsencrypt

  db:
    image: mariadb:latest
    container_name: nginx_proxy_db
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: "${MYSQL_ROOT_PASSWORD}"
      MYSQL_DATABASE: "nginxproxy"
      MYSQL_USER: "npm_nginxproxy"
      MYSQL_PASSWORD: "${MYSQL_PASSWORD}"
    volumes:
      - nginx-proxy-mariandb:/var/lib/mysql
    ports:
      - "3306:3306"

volumes:
  nginx-proxy-data:
  nginx-proxy-letsencrypt:
  nginx-proxy-mariandb: