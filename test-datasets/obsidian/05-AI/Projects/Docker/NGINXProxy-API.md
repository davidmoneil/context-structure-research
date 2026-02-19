---
created: 2025-09-26T21:36
updated: 2026-01-24T09:59
tags:
  - project/kali-scanner
  - depth/deep
  - domain/infrastructure
  - domain/security
  - depth/standard
AI_Summary: This document provides an API reference guide for Nginx Proxy Manager, detailing various endpoints for managing authentication, proxy hosts, SSL certificates, redirection hosts, dead hosts, access lists, user management, settings, Nginx configuration, audit logs, reports, health status, and advanced configurations. It includes information on query parameters, response codes, base URL format, example usage for authentication, accessing resources with a token, and creating a proxy host.
---

```markdown
# Nginx Proxy Manager API Endpoints Reference

## Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/tokens` | Login and get JWT token |
| `POST` | `/api/tokens/refresh` | Refresh existing JWT token |
| `GET` | `/api/users/me` | Get current authenticated user information |

## Proxy Hosts Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/nginx/proxy-hosts` | List all proxy hosts |
| `GET` | `/api/nginx/proxy-hosts/{id}` | Get specific proxy host details |
| `POST` | `/api/nginx/proxy-hosts` | Create new proxy host |
| `PUT` | `/api/nginx/proxy-hosts/{id}` | Update existing proxy host |
| `DELETE` | `/api/nginx/proxy-hosts/{id}` | Delete proxy host |
| `POST` | `/api/nginx/proxy-hosts/{id}/enable` | Enable proxy host |
| `POST` | `/api/nginx/proxy-hosts/{id}/disable` | Disable proxy host |

## SSL Certificates Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/nginx/certificates` | List all SSL certificates |
| `GET` | `/api/nginx/certificates/{id}` | Get specific certificate details |
| `POST` | `/api/nginx/certificates` | Create new SSL certificate (Let's Encrypt or custom) |
| `PUT` | `/api/nginx/certificates/{id}` | Update certificate |
| `DELETE` | `/api/nginx/certificates/{id}` | Delete certificate |
| `POST` | `/api/nginx/certificates/{id}/renew` | Renew Let's Encrypt certificate |
| `POST` | `/api/nginx/certificates/{id}/download` | Download certificate files |

## Redirection Hosts

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/nginx/redirection-hosts` | List all redirection hosts |
| `GET` | `/api/nginx/redirection-hosts/{id}` | Get specific redirection host details |
| `POST` | `/api/nginx/redirection-hosts` | Create new redirection host |
| `PUT` | `/api/nginx/redirection-hosts/{id}` | Update redirection host |
| `DELETE` | `/api/nginx/redirection-hosts/{id}` | Delete redirection host |
| `POST` | `/api/nginx/redirection-hosts/{id}/enable` | Enable redirection host |
| `POST` | `/api/nginx/redirection-hosts/{id}/disable` | Disable redirection host |

## Dead Hosts (404 Pages)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/nginx/dead-hosts` | List all dead hosts |
| `GET` | `/api/nginx/dead-hosts/{id}` | Get specific dead host details |
| `POST` | `/api/nginx/dead-hosts` | Create new dead host (returns 404) |
| `PUT` | `/api/nginx/dead-hosts/{id}` | Update dead host |
| `DELETE` | `/api/nginx/dead-hosts/{id}` | Delete dead host |
| `POST` | `/api/nginx/dead-hosts/{id}/enable` | Enable dead host |
| `POST` | `/api/nginx/dead-hosts/{id}/disable` | Disable dead host |

## Access Lists (IP/Password Protection)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/nginx/access-lists` | List all access lists |
| `GET` | `/api/nginx/access-lists/{id}` | Get specific access list details |
| `POST` | `/api/nginx/access-lists` | Create new access list |
| `PUT` | `/api/nginx/access-lists/{id}` | Update access list |
| `DELETE` | `/api/nginx/access-lists/{id}` | Delete access list |

## User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/users` | List all users |
| `GET` | `/api/users/{id}` | Get specific user details |
| `POST` | `/api/users` | Create new user |
| `PUT` | `/api/users/{id}` | Update user |
| `DELETE` | `/api/users/{id}` | Delete user |
| `POST` | `/api/users/{id}/login` | Login as specific user (admin only) |

## Settings Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/settings` | Get all system settings |
| `POST` | `/api/settings` | Update system settings |
| `GET` | `/api/settings/{key}` | Get specific setting value |
| `PUT` | `/api/settings/{key}` | Update specific setting |

## Nginx Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/nginx/test` | Test nginx configuration |
| `POST` | `/api/nginx/reload` | Reload nginx configuration |
| `GET` | `/api/nginx/logs` | Get nginx access/error logs |
| `GET` | `/api/nginx/stream` | List all stream hosts |
| `POST` | `/api/nginx/stream` | Create new stream host |
| `PUT` | `/api/nginx/stream/{id}` | Update stream host |
| `DELETE` | `/api/nginx/stream/{id}` | Delete stream host |

## Audit Logs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/audit-log` | Get audit log entries |
| `GET` | `/api/audit-log/{id}` | Get specific audit log entry |

## Reports and Statistics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/reports/hosts` | Get host statistics report |
| `GET` | `/api/reports/certificates` | Get certificate statistics report |
| `GET` | `/api/reports/users` | Get user statistics report |

## Health and Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Get application health status |
| `GET` | `/api/version` | Get application version information |
| `GET` | `/api/schema` | Get API schema documentation |

## Advanced Configuration

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/nginx/custom` | List custom nginx configurations |
| `POST` | `/api/nginx/custom` | Create custom nginx configuration |
| `PUT` | `/api/nginx/custom/{id}` | Update custom nginx configuration |
| `DELETE` | `/api/nginx/custom/{id}` | Delete custom nginx configuration |

## Common Query Parameters

Most list endpoints support these query parameters:

- `?expand=certificate,access_list` - Expand related objects
- `?query=search_term` - Search filter
- `?sort=name,-created_on` - Sort results (prefix with `-` for descending)
- `?limit=50&offset=0` - Pagination

## Common Response Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized (invalid/expired token)
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Base URL Format

All endpoints should be prefixed with your NPM instance URL:
```

http://your-server:81/api/ENDPOINT

````

Remember to include the `Authorization: Bearer YOUR_TOKEN` header with all requests except the initial login.

## Example Usage

### Authentication
```bash
# Login
curl -X POST http://localhost:81/api/tokens \
  -H "Content-Type: application/json" \
  -d '{"identity": "admin@example.com", "secret": "password"}'
````

### Using Token

```bash
# Set your token
TOKEN="your_jwt_token_here"

# List proxy hosts
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:81/api/nginx/proxy-hosts
```

### Create Proxy Host

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "domain_names": ["app.example.com"],
       "forward_scheme": "http",
       "forward_host": "192.168.1.100",
       "forward_port": 3000,
       "certificate_id": 0,
       "ssl_forced": false,
       "caching_enabled": false,
       "block_exploits": true,
       "allow_websocket_upgrade": false,
       "access_list_id": 0,
       "advanced_config": "",
       "meta": {}
     }' \
     http://localhost:81/api/nginx/proxy-hosts
```