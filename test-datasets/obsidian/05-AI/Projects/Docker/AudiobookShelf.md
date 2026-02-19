---
created: 2025-07-25T20:09
modified: 2025-07-25T20:33
host: 192.168.1.96
tags:
  - project/tweenagers
  - domain/infrastructure
  - depth/throwaway
  - domain/security
updated: 2026-01-24T10:03
---
services:
  audiobookshelf:
    image: ghcr.io/advplyr/audiobookshelf:latest
    ports:
      - 13378:80
    volumes:
      - /volume1/AudioBooks/:/audiobooks
      - /volume1/docker/audiobookshelf/podcasts:/podcasts
      - /volume1/docker/audiobookshelf/config:/config
      - /volume1/docker/audiobookshelf/metadata:/metadata
      - /volume1/docker/audiobookshelf/backups:/backups
    environment:
      - TZ=America/Denver