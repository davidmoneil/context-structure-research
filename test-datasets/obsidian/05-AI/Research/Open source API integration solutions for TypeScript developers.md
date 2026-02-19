---
created: 2026-01-20T17:01
updated: 2026-01-24T10:44
tags:
  - project/tweenagers
  - depth/deep
  - domain/infrastructure
  - depth/standard
  - project/kali-scanner
---

**Nango emerges as the standout solution** for building multi-tenant API integrations in a TypeScript/Node.js stack. This unified API platform handles OAuth flows, token refresh, rate limiting, and credential management out of the box—the exact pain points that slow down integration development. For developers weighing build-vs-buy decisions, the landscape has consolidated significantly: several promising projects (Supaglue, Fusebit, Revert) have shut down or been acquired, leaving Nango as the primary self-hostable option with **500+ pre-built API connectors** and active development.

The broader ecosystem offers complementary tools depending on your needs. **Activepieces** provides the most affordable path to embedded iPaaS ($800/month vs n8n's $50,000/year). For OAuth-specific challenges, **oauth4webapi** and **openid-client** are the gold standards. And for AI-assisted development, **MCP (Model Context Protocol)** is rapidly becoming the standard for connecting LLMs to integration tools.

---

## Unified API platforms: Nango stands alone

The unified API category—platforms providing a single abstraction layer over multiple third-party APIs—has experienced significant consolidation. Of the major players, only Nango remains viable for self-hosting.

**Nango** (nangohq/nango) is the clear recommendation for TypeScript developers:
- **License**: Elastic License 2.0 (self-hosting allowed, but cannot offer as competing managed service)
- **GitHub**: ~6,000 stars, 189 contributors, multiple commits per week
- **Stack**: 95.5% TypeScript, PostgreSQL backend—perfect fit for Next.js/Supabase projects
- **Pre-built connectors**: 500+ APIs across CRM, accounting, HRIS, ticketing, and more
- **Multi-tenant credentials**: Encrypted storage with automatic token refresh; webhooks notify when credentials become invalid
- **Docker support**: Full docker-compose setup, Helm charts for Kubernetes

The platform evolved from **Pizzly**, an OAuth proxy that Nango adopted in 2022 after Bearer discontinued maintenance. Today it handles the complete integration lifecycle: authorization, token storage, automatic refresh, rate limiting, and data syncing.

For custom integrations, Nango uses a code-first approach with TypeScript. You define providers in `providers.yaml`, write sync scripts for data fetching, and actions for write operations. The learning curve is manageable, and the TypeScript SDK provides end-to-end type safety.

**What happened to the alternatives?**
- **Supaglue**: Archived March 2024, repository read-only
- **Fusebit**: Permanently closed, company defunct
- **Revert**: Acquired by Ampersand, project absorbed into proprietary platform
- **Vessel/Kombo**: Proprietary SaaS only, no self-hosting option

---

## Integration SDKs: Building blocks for custom development

When Nango's unified approach doesn't fit—or when you need granular control—these libraries form a robust foundation for building integrations.

### OAuth libraries

**oauth4webapi** deserves special attention. Created by Filip Skokan (also behind openid-client), it's OpenID Certified, zero-dependency, and works across Node.js, browsers, Deno, and Cloudflare Workers. It supports modern OAuth 2.1 patterns including PKCE and DPoP (Demonstrating Proof-of-Possession). The API is stateless, making per-tenant configuration straightforward.

**openid-client** (same author) excels for OIDC flows with auto-discovery of provider endpoints. Both libraries handle token refresh properly—unlike Passport.js, which leaves refresh handling to developers.

| Library | Weekly Downloads | Token Refresh | Multi-tenant | TypeScript |
|---------|------------------|---------------|--------------|------------|
| oauth4webapi | Growing | Built-in | Flexible | Native |
| openid-client | ~500K | Built-in | Good | Native |
| simple-oauth2 | ~320K | Built-in | Manual | Native |
| Passport.js | ~1.5M | Manual | Manual | Via @types |

### API client generation

**orval** has emerged as the leading generator for TypeScript clients from OpenAPI specs. With 632K weekly npm downloads and commits within hours of this research, it generates type-safe Axios or Fetch clients, TanStack Query hooks, Zod validation schemas, and MSW mocks. The `openapi-typescript` package complements this with runtime-free type generation.

### Rate limiting and retry logic

**Bottleneck** (~1.5M weekly downloads) handles complex rate limiting with priority queues, reservoir patterns, and Redis clustering. Pair it with **axios-retry** (~2M weekly downloads) for exponential backoff on 429 responses. Together, these handle most API throttling scenarios.

```typescript
// Bottleneck example for API rate limiting
const limiter = new Bottleneck({
  maxConcurrent: 1,
  minTime: 6000, // 10 requests per minute
  reservoir: 100,
  reservoirRefreshAmount: 100,
  reservoirRefreshInterval: 60000
});
const throttledApiCall = limiter.wrap(makeApiRequest);
```

---

## Embedded iPaaS platforms compared

For developers who need workflow automation embedded in their product, the licensing landscape is critical. The summary: **n8n's $50,000/year embed license makes it impractical for most startups**, while **Activepieces offers a viable alternative at $800-2,500/month**.

### Activepieces: Best value for embedding

Activepieces uses an **MIT license** for its core, with commercial features for embedding. Key advantages:
- **TypeScript-native**: Pieces (integrations) are npm packages with full type safety
- **500+ connectors**, 60% community-contributed
- **MCP server support**: All pieces available as AI agent tools
- **Embedding features**: White-label admin console, connection cards for OAuth, customizable branding
- **Self-hosted**: Docker-based, can run air-gapped

Embed pricing starts at $800/month (basic embedding) or $2,500/month (full white-label with custom pieces).

### n8n: Powerful but expensive for embedding

n8n has **73,000+ GitHub stars** and 400+ integrations, but its Sustainable Use License explicitly prohibits commercial embedding without an Embed license. That license starts at **$50,000/year**—prohibitive for early-stage products.

The free self-hosted version is excellent for internal automation but cannot be embedded in customer-facing products.

### Windmill: Best for code-first teams

Windmill offers first-class **TypeScript/Deno support** with full LSP in its web IDE. Under AGPLv3, it can be self-hosted but requires a commercial license for SaaS embedding. It's more script-oriented than workflow-oriented—think Retool for backend jobs rather than Zapier.

| Platform | License | Embed Price | Connectors | TypeScript |
|----------|---------|-------------|------------|------------|
| Activepieces | MIT (core) | $800-2,500/mo | 500+ | Native |
| n8n | Sustainable Use | $50,000/year | 400+ | Supported |
| Windmill | AGPLv3 | Contact sales | API-first | Native |
| Automatisch | AGPLv3 | N/A | Limited | Partial |

---

## OAuth and credential management strategies

Multi-tenant credential management is often the hardest part of building integrations. Here's how to approach it.

### Purpose-built solution: Nango

For most teams, **Nango doubles as the credential management layer**. Each "Connection" represents a user's OAuth credentials with tenant isolation built-in. Tokens are encrypted at rest and in transit, refreshed automatically before expiration (at least every 24 hours), and monitored with webhook notifications for failures.

### Database-level encryption for DIY approaches

If building your own credential storage with PostgreSQL/Supabase:

**Supabase Vault** provides transparent column encryption using AES-256 with keys managed by Supabase's backend:

```sql
-- Store encrypted OAuth token
SELECT vault.create_secret(
  'oauth_token_customer_123',
  'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...',
  'OAuth token for customer 123'
);

-- Retrieve via security-definer function
CREATE OR REPLACE FUNCTION get_oauth_token(customer_id TEXT)
RETURNS TEXT AS $$
  SELECT decrypted_secret 
  FROM vault.decrypted_secrets 
  WHERE name = 'oauth_token_' || customer_id;
$$ LANGUAGE sql SECURITY DEFINER;
```

Combine with **Row-Level Security** for tenant isolation:

```sql
ALTER TABLE oauth_tokens ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON oauth_tokens
FOR ALL USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

### Token refresh patterns

Two approaches work well:

**Proactive refresh** (recommended): A cron job refreshes tokens 5 minutes before expiration. This prevents API calls from failing due to expired tokens.

**Lazy refresh**: Check token expiration before each API call, refresh if needed. Simpler but can cause latency spikes.

For standalone secret management, **Infisical** (MIT license, 12,700+ stars) offers a developer-friendly alternative to HashiCorp Vault with Node.js SDK and self-hosting support.

---

## Code generation tools beyond basic codegen

OpenAPI-to-TypeScript generation has matured significantly. The best tools now go far beyond generating types.

**@hey-api/openapi-ts** (successor to the deprecated openapi-typescript-codegen) is used by Vercel and PayPal for production SDK generation. It includes 20+ plugins for Zod validation, TanStack Query hooks, and more.

**orval** generates complete API clients with:
- Axios or Fetch implementations
- React Query/TanStack Query hooks
- Zod schemas for runtime validation
- MSW mocks for testing
- Custom HTTP client support (for credential injection)

For credential management within generated clients, wire in authentication via custom Axios instances:

```typescript
import rateLimit from 'axios-rate-limit';
import axiosRetry from 'axios-retry';

const createTenantClient = (tenantId: string) => {
  const client = axios.create();
  
  // Inject credentials per-tenant
  client.interceptors.request.use(async (config) => {
    const token = await getValidToken(tenantId, 'google-calendar');
    config.headers.Authorization = `Bearer ${token}`;
    return config;
  });
  
  // Add rate limiting and retry
  return rateLimit(axiosRetry(client, {
    retries: 3,
    retryDelay: axiosRetry.exponentialDelay,
  }), { maxRPS: 10 });
};
```

---

## AI-native approaches and Claude Code integration

AI-assisted integration development is rapidly maturing. The key insight: **hybrid approaches outperform both pure traditional and pure AI-heavy development**.

### MCP: The emerging standard

Anthropic's **Model Context Protocol** (donated to Linux Foundation in December 2025) has become the standard for connecting AI agents to tools. Major adoption by OpenAI, Google DeepMind, and IDE tools.

For integration development, MCP enables AI agents to directly interact with APIs through pre-built servers for Google Drive, Slack, GitHub, PostgreSQL, and more. Nango provides an MCP server exposing all 500+ integrations to Claude.

### Claude Code best practices for integrations

**CLAUDE.md is the highest-leverage investment**. This project memory file should include:
- Tech stack and file structure
- Coding standards and patterns
- Common commands and testing approaches
- Example integrations showing preferred patterns

The proven workflow for API integration generation:
1. Use `/init` to auto-generate initial CLAUDE.md
2. Have Claude read relevant files *without* writing code
3. Get a proposed plan before implementation
4. Apply changes incrementally with testing after each step

**Real-world case study**: A developer used Claude Code to refactor 3,000+ line OpenAPI specs, completing 4 days of work that would have taken weeks. The key pattern: have a senior engineer create a gold-standard example, then use Claude to replicate the pattern across other integrations.

### When AI works best (and when it doesn't)

| Scenario | Approach |
|----------|----------|
| Rapid prototyping, MVP development | AI-heavy with human oversight |
| Production systems, complex business logic | Traditional frameworks, AI for assistance |
| API client from good OpenAPI spec | AI generation likely faster |
| Legacy integration, poor documentation | Traditional with AI for exploration |

AI-generated code tends to be **40% more verbose** than necessary and produces **3x more bugs** in production-critical paths. However, for boilerplate—authentication flows, CRUD operations, API client generation—AI offers **10x speed improvements**.

The optimal approach: AI handles boilerplate and common patterns, humans handle architecture, security, and code review.

---

## Decision framework and recommendations

### For rapid prototyping and MVPs
**Use Nango** for OAuth handling and connector management. Supplement with Claude Code for custom integration logic using well-documented OpenAPI specs. This combination provides 500+ ready-made connectors with the flexibility to extend.

### For embedded customer-facing integrations
**Start with Activepieces** at $800/month if you need workflow automation visible to end users. The MIT core allows self-hosting while commercial features provide white-labeling.

### For code-first internal integrations
Combine **oauth4webapi** + **orval** + **Bottleneck** + **BullMQ**. You'll build custom but own every piece. Store credentials with **Supabase Vault** or **Infisical**.

### For maximum AI-assisted development
1. Create comprehensive CLAUDE.md with integration patterns
2. Connect Nango's MCP server to Claude
3. Use orval for type-safe client generation
4. Let Claude handle boilerplate, review all generated code

### Recommended stack for the TypeScript/Next.js/PostgreSQL/Docker environment

| Layer | Recommendation | License | Why |
|-------|----------------|---------|-----|
| Unified API + OAuth | **Nango** (self-hosted or cloud) | Elastic 2.0 | 500+ APIs, TypeScript-native, auto token refresh |
| API client generation | **orval** + **openapi-typescript** | MIT | Full client + hooks generation |
| Rate limiting | **Bottleneck** | MIT | Flexible, Redis clustering support |
| Background jobs | **BullMQ** | MIT | Webhook processing, retry logic |
| Credential encryption | **Supabase Vault** | Apache 2.0 | Native PostgreSQL integration |
| Embedded iPaaS (if needed) | **Activepieces** | MIT (core) | Affordable embedding, TypeScript pieces |

---

## Conclusion

The integration tools landscape has consolidated around a few strong options. **Nango is the clear choice** for TypeScript developers needing multi-tenant OAuth management and pre-built connectors—it's the only actively maintained open-source unified API platform with substantial connector coverage. Its evolution from Pizzly to a full integration infrastructure platform reflects what developers actually need: not just OAuth flows, but the complete credential lifecycle.

For embedding workflow automation in products, **Activepieces' MIT-licensed core** offers a dramatically more accessible entry point than n8n's $50,000 annual fee. And for AI-assisted development, **MCP is the standard to adopt now**—Nango, Activepieces, and major AI providers all support it.

The most effective path forward combines these tools strategically: Nango for the connector layer, orval for type-safe client generation, and Claude Code with a well-crafted CLAUDE.md for rapid iteration. This hybrid approach leverages automation where it excels while maintaining the architectural control that production systems require.