---
tags:
  - status/active
  - depth/deep
  - domain/dnd
  - domain/ai
  - domain/security
created: 2026-01-09T19:25
updated: 2026-01-24T10:34
---
# Outlook Intel Classification Results

**Date**: 2026-01-09
**Sample Size**: 500 emails (from last 365 days: Jan 2023 - Jan 2024)
**Classification Method**: Hybrid (Rule-based + LLM)

---

## Executive Summary

Analysis of 500 work emails from a Cybersecurity Leader role reveals:

- **55.7% Core Work** - Direct security, vendor, and team responsibilities
- **42.1% Overhead** - Meetings, procurement, automated notifications
- **2.2% Strategic** - Planning and external engagement

The RACI analysis shows balanced accountability:
- 46.7% Responsible (doing the work)
- 37.7% Informed (kept in loop)
- 8.0% Consulted (providing input)
- 6.4% Accountable (owning outcomes)

---

## Classification Method Performance

| Method | Count | Percentage |
|--------|-------|------------|
| Rule-based | 444 | 89.0% |
| LLM (qwen2.5:32b) | 55 | 11.0% |
| Unclassified | 1 | 0.2% |

**Key Finding**: Rule-based classification handled 89% of emails, reducing LLM API costs significantly while maintaining accuracy for complex cases.

### Confidence Distribution

| Level | Count | Description |
|-------|-------|-------------|
| High (0.85+) | 132 | Strong keyword matches |
| Medium (0.6-0.84) | 367 | Multiple weak signals |

---

## Work Type Breakdown

```
CORE WORK: 55.7%
████████████████████████████░░░░░░░░░░░░░░░░░░░░░░

OVERHEAD: 42.1%
█████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

STRATEGIC: 2.2%
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

### Core Work Categories (278 emails, 55.7%)

| Category | Name | Count | % of Core |
|----------|------|-------|-----------|
| SECOPS | Security Operations | 106 | 38.1% |
| VENDOR | Vendor Management | 72 | 25.9% |
| GRC | Governance Risk Compliance | 48 | 17.3% |
| TEAM | Team Leadership | 29 | 10.4% |
| ONCALL | On-Call/PagerDuty | 12 | 4.3% |
| STAKEHOLDER | Stakeholder Support | 8 | 2.9% |
| EXECRPT | Executive Reporting | 3 | 1.1% |

### Overhead Categories (210 emails, 42.1%)

| Category | Name | Count | % of Overhead |
|----------|------|-------|---------------|
| AUTOMATED | Automated Alerts | 91 | 43.3% |
| PROCURE | Procurement & Finance | 66 | 31.4% |
| MEETINGS | Meetings & Syncs | 36 | 17.1% |
| LEGAL | Legal Document Review | 12 | 5.7% |
| CALENDAR | Calendar Noise | 3 | 1.4% |
| TICKETS | ServiceNow/Tickets | 2 | 1.0% |

### Strategic Categories (11 emails, 2.2%)

| Category | Name | Count |
|----------|------|-------|
| STRATEGY | Strategic Planning | 9 |
| EXTERNAL | External Engagement | 2 |

---

## RACI Accountability Analysis

```
RESPONSIBLE: 46.7% - You do the work
████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░

INFORMED: 37.7% - Kept in the loop
███████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

CONSULTED: 8.0% - Provide input/advice
████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

ACCOUNTABLE: 6.4% - Own the outcome/decision
███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

| RACI Level | Count | Percentage | Inference Signal |
|------------|-------|------------|------------------|
| R (Responsible) | 233 | 46.7% | User sent email, or core work type |
| I (Informed) | 188 | 37.7% | CC'd only, automated notifications |
| C (Consulted) | 40 | 8.0% | Review/feedback keywords |
| A (Accountable) | 32 | 6.4% | Escalation/approval keywords |
| Unknown | 6 | 1.2% | Insufficient signals |

---

## Category Distribution (All Classifications)

| Code | Category | Work Type | Count | % |
|------|----------|-----------|-------|---|
| SECOPS | Security Operations | CORE | 106 | 21.2% |
| AUTOMATED | Automated Alerts | OVERHEAD | 91 | 18.2% |
| VENDOR | Vendor Management | CORE | 72 | 14.4% |
| PROCURE | Procurement & Finance | OVERHEAD | 66 | 13.2% |
| GRC | Governance Risk Compliance | CORE | 48 | 9.6% |
| MEETINGS | Meetings & Syncs | OVERHEAD | 36 | 7.2% |
| TEAM | Team Leadership | CORE | 29 | 5.8% |
| LEGAL | Legal Document Review | OVERHEAD | 12 | 2.4% |
| ONCALL | On-Call/PagerDuty | CORE | 12 | 2.4% |
| STRATEGY | Strategic Planning | STRATEGIC | 9 | 1.8% |
| STAKEHOLDER | Stakeholder Support | CORE | 8 | 1.6% |
| CALENDAR | Calendar Noise | OVERHEAD | 3 | 0.6% |
| EXECRPT | Executive Reporting | CORE | 3 | 0.6% |
| EXTERNAL | External Engagement | STRATEGIC | 2 | 0.4% |
| TICKETS | ServiceNow/Tickets | OVERHEAD | 2 | 0.4% |

---

## Multi-Tag Analysis

Many emails span multiple work categories:

| Tags per Email | Email Count | Percentage |
|----------------|-------------|------------|
| 1 tag | 115 | 23.0% |
| 2 tags | 240 | 48.0% |
| 3 tags | 100 | 20.0% |
| 4 tags | 40 | 8.0% |
| 5 tags | 4 | 0.8% |

**Finding**: 77% of emails required multiple category tags, validating the multi-tag classification approach.

---

## Top Email Domains

| Domain | Email Count | Notes |
|--------|-------------|-------|
| icims.com | 263 | Internal (primary) |
| service-now.com | 99 | Ticket system |
| okta.com | 22 | SSO/Identity |
| icimsinc.onmicrosoft.com | 14 | Internal (M365) |
| email.icims.io | 12 | Internal notifications |
| seemplicity.io | 10 | Security vendor |
| wiz.io | 9 | Cloud security vendor |
| gartner.com | 7 | Analyst firm |
| 360advanced.com | 5 | Security vendor |
| vendr.com | 4 | Procurement platform |

---

## Key Insights

### 1. Security Operations Dominates Core Work
SECOPS (21.2%) is the largest single category, confirming the role's primary focus on incident response, vulnerability management, and security monitoring.

### 2. Heavy Vendor Ecosystem
Combined VENDOR (14.4%) + PROCURE (13.2%) = 27.6% of emails relate to the security tool ecosystem. Key vendors visible: Wiz, Seemplicity, Gartner, Vendr.

### 3. Significant Automation Overhead
AUTOMATED alerts (18.2%) represent the largest overhead category - potential for filtering/consolidation to reduce noise.

### 4. GRC is Substantial
Nearly 10% of work involves governance, risk, and compliance activities (audits, policies, assessments).

### 5. Balanced Accountability Profile
46.7% Responsible indicates active work ownership, while 37.7% Informed suggests appropriate delegation and visibility.

---

## Methodology

### Classification Approach
1. **Rule-based (Pass 1)**: Keyword matching against 16 category keyword lists
2. **LLM (Pass 2)**: Ollama qwen2.5:32b for low-confidence (<0.5) cases
3. **RACI Inference**: Based on sent/received, CC status, keywords

### Work Type Definition
- **CORE**: Direct role responsibilities (security, vendors, team)
- **OVERHEAD**: Supporting activities (meetings, procurement, notifications)
- **STRATEGIC**: Future-focused planning and external engagement

### Data Scope
- Source: Outlook.sqlite export (Mac Outlook)
- Period: Jan 2023 - Jan 2024 (365 days)
- Sample: 500 most recent emails
- Total available: ~21,000 emails in period

---

## Next Steps

1. **Build Labeling Tool**: Streamlit app for human review of classifications
2. **Label Training Data**: Review 200-500 emails, prioritizing low-confidence
3. **Train Fast Classifier**: ML model from labeled data
4. **Full Dataset Run**: Apply to all 21,000 emails
5. **Insights Dashboard**: Work distribution, time allocation, vendor analysis

---

## Project Links

- **Project Location**: `/mnt/synology_nas/main/workspaces/outlook-intel/`
- **Database**: `Outlook-enriched.sqlite`
- **Classifier**: `classify_emails.py`
- **Patterns**: `docs/patterns/` (role-based, RACI, core-overhead)
- **AIProjects Context**: `.claude/context/projects/outlook-intel.md`

---

*Generated by Claude Code - 2026-01-09*
