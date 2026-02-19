---
created: 2026-01-12T16:00
updated: 2026-01-24T10:34
status: planning
tags:
  - project/ciso-book
  - depth/deep
  - domain/dnd
  - domain/ai
  - domain/security
---

# SpiderFoot Phased Module System - Implementation Plan

## Overview

This plan implements a phased SpiderFoot module system that:
1. Runs fast, high-confidence modules first (Phase 1)
2. Triggers cloud_enum and Nuclei after Phase 1
3. Runs deeper scanning modules in parallel (Phase 2)
4. Provides manual expansion buttons for specific assets

---

## Phase Definitions

### Phase 1: Fast Discovery (~15-30 minutes)
**Goal:** Find all domains, subdomains, IPs owned by target with HIGH confidence.

| Module | Purpose | Category |
|--------|---------|----------|
| `sfp_dnsresolve` | Resolve all discovered hosts | DNS |
| `sfp_dnsraw` | MX, TXT, SPF records | DNS |
| `sfp_crt` | Certificate transparency (subdomains) | Certs |
| `sfp_certspotter` | More cert transparency | Certs |
| `sfp_dnsdumpster` | Passive subdomain discovery | Subdomain |
| `sfp_sublist3r` | Subdomain enumeration | Subdomain |
| `sfp_projectdiscovery` | Chaos subdomain database | Subdomain |
| `sfp_whois` | Domain ownership verification | Ownership |
| `sfp_ripe` | Netblock ownership (IP ranges) | Ownership |
| `sfp_arin` | ARIN registry (Americas) | Ownership |
| `sfp_bgpview` | BGP/ASN ownership | Ownership |
| `sfp_sslcert` | SSL cert details | Certs |
| `sfp_webserver` | Web server banners | Fingerprint |
| `sfp_webframework` | Detect frameworks | Fingerprint |
| `sfp_tool_wappalyzer` | Technology fingerprinting | Fingerprint |
| `sfp_s3bucket` | Quick S3 bucket check | Cloud |
| `sfp_azureblobstorage` | Quick Azure blob check | Cloud |
| `sfp_googleobjectstorage` | Quick GCP bucket check | Cloud |
| `sfp_grayhatwarfare` | Known open buckets database | Cloud |

**Total: 19 modules**

**After Phase 1 completes:**
- Extract keywords → Start cloud_enum (parallel)
- Extract hosts/IPs → Start Nuclei with `tech-detect,exposed-panels` tags (parallel)
- Start Phase 2 SpiderFoot modules (parallel)

---

### Phase 2: Deep Infrastructure (~30-60 minutes, parallel)
**Goal:** Port scanning, service detection, deeper fingerprinting.

| Module | Purpose | Category |
|--------|---------|----------|
| `sfp_portscan_tcp` | Common port scanning | Ports |
| `sfp_tool_whatweb` | Detailed web fingerprinting | Fingerprint |
| `sfp_tool_cmseek` | CMS detection | Fingerprint |
| `sfp_tool_wafw00f` | WAF detection | Fingerprint |
| `sfp_strangeheaders` | Unusual HTTP headers | Headers |
| `sfp_cookie` | Cookie analysis | Headers |
| `sfp_dnsbrute` | DNS brute-forcing | DNS Deep |
| `sfp_dnscommonsrv` | SRV record brute-force | DNS Deep |

**Total: 8 modules**

---

### Phase 3: Manual Expansion (User-Triggered)
**Goal:** Deep scans on specific assets selected by user.

| Button Label | Modules | Use Case |
|--------------|---------|----------|
| Deep Port Scan | `sfp_portscan_tcp` (extended), `sfp_tool_nmap` | Full port range on specific host |
| SSL Analysis | `sfp_tool_testsslsh` | Check Heartbleed, weak ciphers |
| Code Repos | `sfp_github`, `sfp_searchcode`, `sfp_tool_trufflehog` | Found dev subdomain |
| Historical Data | `sfp_archiveorg`, `sfp_commoncrawl` | Wayback Machine |
| Subdomain Takeover | `sfp_subdomain_takeover` | Check hijackable subdomains |

---

## Architecture Changes

### Database Schema

**Option A: Use existing JSONB (Recommended - No migration needed)**

Extend `spiderfoot_config` JSONB column:
```json
{
  "use_case": "custom",
  "phase1_modules": ["sfp_dnsresolve", "sfp_crt", ...],
  "phase2_modules": ["sfp_portscan_tcp", ...],
  "current_spiderfoot_phase": 1,
  "phase1_scan_id": "uuid",
  "phase2_scan_id": "uuid"
}
```

**Option B: New columns (If we want explicit schema)**

```sql
-- Migration 008_spiderfoot_phases.sql
ALTER TABLE osint.campaigns
  ADD COLUMN spiderfoot_phase1_modules TEXT[] DEFAULT NULL,
  ADD COLUMN spiderfoot_phase2_modules TEXT[] DEFAULT NULL,
  ADD COLUMN spiderfoot_current_phase INTEGER DEFAULT 1;

ALTER TABLE osint.campaign_tools
  ADD COLUMN sub_phase VARCHAR(50) DEFAULT NULL,
  ADD COLUMN sub_phase_scan_id VARCHAR(255) DEFAULT NULL;
```

**Recommendation:** Start with Option A (JSONB), migrate to Option B if needed later.

---

### Backend Changes

#### 1. Module Presets (New File)
**File:** `/dashboard/app/services/module_presets.py`

```python
"""SpiderFoot module presets for phased scanning."""

PHASE1_MODULES = [
    # DNS & Resolution
    "sfp_dnsresolve",
    "sfp_dnsraw",

    # Certificate Transparency
    "sfp_crt",
    "sfp_certspotter",
    "sfp_sslcert",

    # Subdomain Discovery
    "sfp_dnsdumpster",
    "sfp_sublist3r",
    "sfp_projectdiscovery",

    # Ownership/Registration
    "sfp_whois",
    "sfp_ripe",
    "sfp_arin",
    "sfp_bgpview",

    # Fingerprinting (Fast)
    "sfp_webserver",
    "sfp_webframework",
    "sfp_tool_wappalyzer",

    # Cloud Discovery
    "sfp_s3bucket",
    "sfp_azureblobstorage",
    "sfp_googleobjectstorage",
    "sfp_grayhatwarfare",
]

PHASE2_MODULES = [
    # Port Scanning
    "sfp_portscan_tcp",

    # Deep Fingerprinting
    "sfp_tool_whatweb",
    "sfp_tool_cmseek",
    "sfp_tool_wafw00f",

    # Headers & Cookies
    "sfp_strangeheaders",
    "sfp_cookie",

    # DNS Deep
    "sfp_dnsbrute",
    "sfp_dnscommonsrv",
]

MANUAL_EXPANSION_MODULES = {
    "deep_port_scan": ["sfp_portscan_tcp", "sfp_tool_nmap"],
    "ssl_analysis": ["sfp_tool_testsslsh"],
    "code_repos": ["sfp_github", "sfp_searchcode", "sfp_tool_trufflehog"],
    "historical": ["sfp_archiveorg", "sfp_commoncrawl"],
    "subdomain_takeover": ["sfp_subdomain_takeover"],
}

# Module descriptions for UI
MODULE_DESCRIPTIONS = {
    "sfp_dnsresolve": "Resolve hostnames to IP addresses",
    "sfp_crt": "Certificate transparency logs (crt.sh)",
    "sfp_whois": "WHOIS domain registration lookup",
    "sfp_s3bucket": "Amazon S3 bucket discovery",
    # ... etc
}

# Presets for dropdown
SCAN_PRESETS = {
    "fast_discovery": {
        "name": "Fast Discovery",
        "description": "Quick recon: DNS, certs, subdomains, basic fingerprinting (~15-30 min)",
        "phase1_modules": PHASE1_MODULES,
        "phase2_modules": [],
        "auto_phase2": False,
    },
    "standard": {
        "name": "Standard (Recommended)",
        "description": "Full pipeline: Fast discovery → cloud_enum → Nuclei → Deep scan (~1-2 hours)",
        "phase1_modules": PHASE1_MODULES,
        "phase2_modules": PHASE2_MODULES,
        "auto_phase2": True,
    },
    "deep_scan": {
        "name": "Deep Scan",
        "description": "All modules including port scanning and brute-forcing (~2-4 hours)",
        "phase1_modules": PHASE1_MODULES + PHASE2_MODULES,
        "phase2_modules": [],
        "auto_phase2": False,
    },
    "custom": {
        "name": "Custom",
        "description": "Select individual modules",
        "phase1_modules": [],
        "phase2_modules": [],
        "auto_phase2": False,
    },
}
```

#### 2. Campaign Service Changes
**File:** `/dashboard/app/services/campaign_service.py`

**Changes to `_execute_spiderfoot()`:**

```python
async def _execute_spiderfoot(campaign_id: str, phase: int = 1) -> Dict[str, Any]:
    """
    Start a SpiderFoot scan for a specific phase.

    Phase 1: Fast discovery modules
    Phase 2: Deep scanning modules (runs after Phase 1 completes)
    """
    settings = get_settings()
    campaign = await get_campaign(campaign_id)

    # Get phase-specific modules from config
    sf_config = campaign.get('spiderfoot_config') or {}
    if isinstance(sf_config, str):
        sf_config = json.loads(sf_config)

    if phase == 1:
        modules = sf_config.get('phase1_modules', PHASE1_MODULES)
        scan_name = f"Campaign {campaign['name']} - Phase 1"
    else:
        modules = sf_config.get('phase2_modules', PHASE2_MODULES)
        scan_name = f"Campaign {campaign['name']} - Phase 2"

    if not modules:
        return {"success": True, "scan_id": None, "skipped": True}

    # Start scan with specific modules
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{settings.spiderfoot_url}/startscan",
            data={
                "scanname": scan_name,
                "scantarget": campaign['target'],
                "modulelist": ",".join(modules),  # KEY CHANGE: Specific modules
                "usecase": "",  # Empty when using modulelist
                "typelist": "",
            },
            headers={"Accept": "application/json"}
        )

        # ... rest of existing logic
```

**New function for Phase 2 trigger:**

```python
async def start_spiderfoot_phase2(campaign_id: str) -> bool:
    """
    Start SpiderFoot Phase 2 modules.
    Called after Phase 1 completes and cloud_enum/Nuclei are triggered.
    """
    campaign = await get_campaign(campaign_id)
    sf_config = campaign.get('spiderfoot_config') or {}

    if not sf_config.get('auto_phase2', True):
        return False

    phase2_modules = sf_config.get('phase2_modules', PHASE2_MODULES)
    if not phase2_modules:
        return False

    # Update config to track phase
    sf_config['current_spiderfoot_phase'] = 2
    await update_campaign_spiderfoot_config(campaign_id, sf_config)

    # Start Phase 2 scan
    result = await _execute_spiderfoot(campaign_id, phase=2)

    if result['success']:
        await add_campaign_event(
            campaign_id, "phase_started",
            f"SpiderFoot Phase 2 started with {len(phase2_modules)} modules",
            tool_name="spiderfoot",
            metadata={"phase": 2, "modules": phase2_modules}
        )

    return result['success']
```

#### 3. Normalizer Integration
**File:** `/normalizer/src/main.py`

When SpiderFoot Phase 1 completes:
1. Extract keywords → trigger cloud_enum
2. Extract hosts → trigger Nuclei (tech-detect only)
3. Trigger SpiderFoot Phase 2 (parallel)

```python
# In sync_spiderfoot(), after detecting completion:
if campaign and scan_phase == 1:
    # Phase 1 complete - trigger parallel Phase 2 + cloud_enum + Nuclei
    db_manager.update_campaign_spiderfoot_phase(campaign['id'], phase=2)
    # Dashboard orchestration loop will pick up Phase 2
```

---

### Frontend Changes

#### 1. Campaign Creation Form
**File:** `/dashboard/app/templates/campaign_create.html`

Add scan preset selector and module configuration:

```html
<!-- SpiderFoot Configuration Section -->
<div id="spiderfoot-config" class="mt-4 space-y-4">
    <h3 class="text-lg font-medium text-white">SpiderFoot Configuration</h3>

    <!-- Scan Preset Dropdown -->
    <div>
        <label class="block text-sm text-gray-300 mb-2">Scan Preset</label>
        <select name="spiderfoot_preset" id="spiderfoot-preset"
                class="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white"
                onchange="updateModuleSelection(this.value)">
            <option value="standard" selected>Standard (Recommended) - ~1-2 hours</option>
            <option value="fast_discovery">Fast Discovery - ~15-30 min</option>
            <option value="deep_scan">Deep Scan - ~2-4 hours</option>
            <option value="custom">Custom - Select modules</option>
        </select>
        <p id="preset-description" class="text-xs text-gray-500 mt-1">
            Full pipeline: Fast discovery → cloud_enum → Nuclei → Deep scan
        </p>
    </div>

    <!-- Phase 2 Auto-trigger -->
    <div class="flex items-center gap-2">
        <input type="checkbox" name="auto_phase2" id="auto-phase2" checked
               class="rounded bg-gray-700 border-gray-600">
        <label for="auto-phase2" class="text-sm text-gray-300">
            Auto-run Phase 2 (deep scanning) after Phase 1 completes
        </label>
    </div>

    <!-- Custom Module Selection (hidden by default) -->
    <div id="custom-modules" class="hidden">
        <div class="grid grid-cols-2 gap-4">
            <!-- Phase 1 Modules -->
            <div>
                <h4 class="text-sm font-medium text-gray-300 mb-2">Phase 1: Fast Discovery</h4>
                <div class="space-y-1 max-h-64 overflow-y-auto bg-gray-900 rounded p-2">
                    {% for module in phase1_modules %}
                    <label class="flex items-start gap-2 text-xs">
                        <input type="checkbox" name="phase1_modules" value="{{ module.name }}"
                               checked class="mt-0.5 rounded bg-gray-700 border-gray-600">
                        <div>
                            <span class="text-gray-300">{{ module.name }}</span>
                            <span class="text-gray-500 block">{{ module.description }}</span>
                        </div>
                    </label>
                    {% endfor %}
                </div>
            </div>

            <!-- Phase 2 Modules -->
            <div>
                <h4 class="text-sm font-medium text-gray-300 mb-2">Phase 2: Deep Scanning</h4>
                <div class="space-y-1 max-h-64 overflow-y-auto bg-gray-900 rounded p-2">
                    {% for module in phase2_modules %}
                    <label class="flex items-start gap-2 text-xs">
                        <input type="checkbox" name="phase2_modules" value="{{ module.name }}"
                               checked class="mt-0.5 rounded bg-gray-700 border-gray-600">
                        <div>
                            <span class="text-gray-300">{{ module.name }}</span>
                            <span class="text-gray-500 block">{{ module.description }}</span>
                        </div>
                    </label>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function updateModuleSelection(preset) {
    const customSection = document.getElementById('custom-modules');
    const description = document.getElementById('preset-description');
    const autoPhase2 = document.getElementById('auto-phase2');

    const presets = {
        'fast_discovery': {
            desc: 'Quick recon: DNS, certs, subdomains, basic fingerprinting (~15-30 min)',
            autoPhase2: false
        },
        'standard': {
            desc: 'Full pipeline: Fast discovery → cloud_enum → Nuclei → Deep scan (~1-2 hours)',
            autoPhase2: true
        },
        'deep_scan': {
            desc: 'All modules including port scanning and brute-forcing (~2-4 hours)',
            autoPhase2: false
        },
        'custom': {
            desc: 'Select individual modules below',
            autoPhase2: true
        }
    };

    description.textContent = presets[preset].desc;
    autoPhase2.checked = presets[preset].autoPhase2;
    customSection.classList.toggle('hidden', preset !== 'custom');
}
</script>
```

#### 2. Campaign Detail - Phase Display
**File:** `/dashboard/app/templates/campaign_detail.html`

Update the stepper to show SpiderFoot phases:

```html
<!-- Enhanced Pipeline Progress -->
<div class="flex items-center justify-between relative">
    <!-- SpiderFoot Phase 1 -->
    <div class="flex flex-col items-center z-10">
        <div class="w-10 h-10 rounded-full flex items-center justify-center
            {% if sf_phase1_status == 'COMPLETED' %}bg-green-600
            {% elif sf_phase1_status == 'RUNNING' %}bg-blue-600 animate-pulse
            {% else %}bg-gray-700{% endif %}">
            1
        </div>
        <div class="mt-2 text-center">
            <div class="text-sm text-white">SpiderFoot</div>
            <div class="text-xs text-gray-400">Phase 1</div>
        </div>
    </div>

    <!-- Connector -->
    <div class="flex-1 h-0.5 bg-gray-600 mx-2"></div>

    <!-- cloud_enum (parallel with Phase 2) -->
    <div class="flex flex-col items-center z-10">
        <!-- ... -->
    </div>

    <!-- Connector -->
    <div class="flex-1 h-0.5 bg-gray-600 mx-2"></div>

    <!-- Nuclei (parallel with Phase 2) -->
    <div class="flex flex-col items-center z-10">
        <!-- ... -->
    </div>

    <!-- SpiderFoot Phase 2 (shown below main pipeline) -->
</div>

<!-- Phase 2 indicator (runs parallel) -->
{% if campaign.spiderfoot_config.phase2_modules %}
<div class="mt-4 pt-4 border-t border-gray-700">
    <div class="flex items-center gap-2 text-sm text-gray-400">
        <span class="w-2 h-2 rounded-full
            {% if sf_phase2_status == 'COMPLETED' %}bg-green-400
            {% elif sf_phase2_status == 'RUNNING' %}bg-blue-400 animate-pulse
            {% else %}bg-gray-600{% endif %}"></span>
        <span>SpiderFoot Phase 2 (Deep Scanning)</span>
        {% if sf_phase2_status == 'RUNNING' %}
        <span class="text-xs text-blue-400">Running in parallel...</span>
        {% endif %}
    </div>
</div>
{% endif %}
```

#### 3. Manual Expansion Buttons
**File:** `/dashboard/app/templates/campaign_detail.html`

Add expansion section after pipeline:

```html
<!-- Manual Expansion Section -->
{% if campaign.status.value in ['RUNNING', 'COMPLETED'] %}
<div class="bg-gray-800 rounded-lg p-6 mt-6">
    <h2 class="text-lg font-semibold mb-4">Manual Expansion</h2>
    <p class="text-sm text-gray-400 mb-4">
        Run additional scans on discovered assets. Select assets below and choose an expansion type.
    </p>

    <!-- Asset Selection -->
    <div class="mb-4">
        <label class="block text-sm text-gray-300 mb-2">Select Assets (or leave empty for all)</label>
        <select name="expansion_targets" multiple
                class="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white h-32">
            {% for host in discovered_hosts[:50] %}
            <option value="{{ host }}">{{ host }}</option>
            {% endfor %}
        </select>
    </div>

    <!-- Expansion Buttons -->
    <div class="flex flex-wrap gap-2">
        <form method="POST" action="/campaigns/{{ campaign.id }}/expand/deep_port_scan" class="inline">
            <button type="submit" class="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded">
                🔍 Deep Port Scan
            </button>
        </form>

        <form method="POST" action="/campaigns/{{ campaign.id }}/expand/ssl_analysis" class="inline">
            <button type="submit" class="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded">
                🔒 SSL Analysis
            </button>
        </form>

        <form method="POST" action="/campaigns/{{ campaign.id }}/expand/code_repos" class="inline">
            <button type="submit" class="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded">
                💻 Code Repos
            </button>
        </form>

        <form method="POST" action="/campaigns/{{ campaign.id }}/expand/historical" class="inline">
            <button type="submit" class="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded">
                📜 Historical Data
            </button>
        </form>

        <form method="POST" action="/campaigns/{{ campaign.id }}/expand/subdomain_takeover" class="inline">
            <button type="submit" class="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded">
                ⚠️ Subdomain Takeover
            </button>
        </form>
    </div>
</div>
{% endif %}
```

#### 4. New Router Endpoint
**File:** `/dashboard/app/routers/campaigns.py`

```python
@router.post("/{campaign_id}/expand/{expansion_type}", response_class=HTMLResponse)
async def expand_campaign(
    request: Request,
    campaign_id: str,
    expansion_type: str,
    targets: list[str] = Form(default=[])
):
    """Run manual expansion scan on campaign assets."""
    from ..services.module_presets import MANUAL_EXPANSION_MODULES

    if expansion_type not in MANUAL_EXPANSION_MODULES:
        raise HTTPException(status_code=400, detail="Invalid expansion type")

    modules = MANUAL_EXPANSION_MODULES[expansion_type]
    success = await run_expansion_scan(campaign_id, modules, targets)

    if not success:
        return HTMLResponse(
            content=f'<div class="text-red-400">Failed to start {expansion_type}</div>',
            status_code=200
        )

    return RedirectResponse(url=f"/campaigns/{campaign_id}", status_code=303)
```

---

## Execution Flow Diagram

```
Campaign Started
       │
       ▼
┌──────────────────┐
│ SpiderFoot       │
│ Phase 1          │  ~15-30 min
│ (19 modules)     │
└────────┬─────────┘
         │
         │ Phase 1 Complete
         │
         ▼
    ┌────┴────┬────────────┐
    │         │            │
    ▼         ▼            ▼
┌────────┐ ┌────────┐ ┌────────────┐
│cloud_  │ │Nuclei  │ │SpiderFoot  │
│enum    │ │(tech   │ │Phase 2     │
│        │ │detect) │ │(8 modules) │  All run in PARALLEL
└────┬───┘ └────┬───┘ └─────┬──────┘
     │         │            │
     └────┬────┴────────────┘
          │
          ▼
    All Complete
          │
          ▼
┌──────────────────┐
│ Manual Expansion │  User-triggered
│ (optional)       │
└──────────────────┘
```

---

## Implementation Sequence

### Step 1: Backend Foundation
1. Create `module_presets.py` with module lists and presets
2. Update `schemas.py` - add `spiderfoot_preset`, `phase1_modules`, `phase2_modules` to `CampaignCreateRequest`
3. Update `campaign_service.py`:
   - Modify `_execute_spiderfoot()` to accept phase parameter
   - Add `start_spiderfoot_phase2()` function
   - Update `handle_spiderfoot_completion()` to trigger parallel execution

### Step 2: Database (Optional)
1. Create migration if using explicit columns (or skip if using JSONB)
2. Update `database.py` functions to handle new fields

### Step 3: Campaign Creation UI
1. Update `campaign_create.html` with preset selector
2. Add JavaScript for dynamic module selection
3. Update `campaigns.py` router to handle new form fields

### Step 4: Campaign Detail UI
1. Update stepper to show SpiderFoot phases
2. Add Phase 2 status indicator
3. Add manual expansion buttons section

### Step 5: Normalizer Integration
1. Update normalizer to detect Phase 1 vs Phase 2 completion
2. Trigger appropriate next steps based on phase

### Step 6: Testing
1. Test preset selection
2. Test custom module selection
3. Test Phase 1 → Phase 2 → cloud_enum/Nuclei flow
4. Test manual expansion buttons

---

## API Changes Summary

| Endpoint | Method | Change |
|----------|--------|--------|
| `/campaigns` | POST | Add `spiderfoot_preset`, `phase1_modules[]`, `phase2_modules[]`, `auto_phase2` |
| `/campaigns/{id}/expand/{type}` | POST | NEW - Run expansion scan |
| `/campaigns/{id}/start-phase2` | POST | NEW - Manually trigger Phase 2 |

---

## Questions/Decisions Needed

1. **Module validation**: Should we validate module names against SpiderFoot's actual module list, or trust user input?

2. **Phase 2 failure handling**: If Phase 2 fails, should it affect overall campaign status?

3. **Expansion scan tracking**: Should expansion scans be tracked as separate campaign_tools entries or as events?

4. **Nuclei template selection**: Should Phase 1 Nuclei only run `tech-detect,exposed-panels`, then full templates after Phase 2?

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `/dashboard/app/services/module_presets.py` | CREATE | Module definitions and presets |
| `/dashboard/app/services/campaign_service.py` | MODIFY | Phase-aware SpiderFoot execution |
| `/dashboard/app/models/schemas.py` | MODIFY | Add new request fields |
| `/dashboard/app/routers/campaigns.py` | MODIFY | Handle new form fields, add expansion endpoint |
| `/dashboard/app/templates/campaign_create.html` | MODIFY | Preset selector, module checkboxes |
| `/dashboard/app/templates/campaign_detail.html` | MODIFY | Phase display, expansion buttons |
| `/dashboard/app/templates/partials/campaign_progress.html` | MODIFY | Phase-aware progress display |
| `/normalizer/src/main.py` | MODIFY | Phase-aware completion handling |
| `/database/migrations/008_spiderfoot_phases.sql` | CREATE (optional) | Schema changes if needed |

---

## Estimated Effort

| Phase | Tasks | Estimate |
|-------|-------|----------|
| Backend Foundation | Presets, service changes | 2-3 hours |
| Campaign Creation UI | Form updates, JS | 1-2 hours |
| Campaign Detail UI | Phase display, buttons | 1-2 hours |
| Normalizer Integration | Phase detection | 1 hour |
| Testing | End-to-end testing | 1-2 hours |
| **Total** | | **6-10 hours** |
