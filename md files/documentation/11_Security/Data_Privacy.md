# MemeGPT — Data Privacy

> **Document Version:** 1.0 · **Last Updated:** 2026-08-02

---

## Purpose

Dedicated data privacy documentation covering GDPR compliance, data handling policies, and privacy-by-design implementation.

---

## Privacy-by-Design Principles

| # | Principle | MemeGPT Implementation |
|---|---|---|
| 1 | **Proactive, not reactive** | Privacy considered from day 1, not added later |
| 2 | **Default privacy** | NSFW off, no tracking, no account required |
| 3 | **Embedded in design** | Anonymous search, hashed queries, no PII logs |
| 4 | **Full functionality** | No features require privacy sacrifice |
| 5 | **End-to-end security** | HTTPS, secret rotation, minimal data collection |
| 6 | **Transparency** | Clear privacy policy at `/privacy` |
| 7 | **User-centric** | Data export and deletion on request |

---

## Data Classification

| Category | Data | Classification | Stored | Retention |
|---|---|---|---|---|
| Meme catalog | Name, image URLs, tags | Public | Indefinite | N/A |
| Search queries | Raw text (hashed) | Internal | 90 days | Auto-purge |
| Feedback signals | Meme ID + action | Internal | 90 days | Aggregated |
| Session IDs | Random string | Anonymous | Session only | Auto-expire |
| IP addresses | Masked in logs | PII-adjacent | 24 hours | Auto-purge |
| User email | If registered (Phase 3) | PII | Until deletion | On request |

---

## GDPR Compliance

### Data Subject Rights

| Right | Endpoint | Implementation |
|---|---|---|
| Right to access | `GET /api/v1/privacy/export?session_id=X` | Export all data as JSON |
| Right to deletion | `DELETE /api/v1/privacy/delete?session_id=X` | Delete all session data |
| Right to portability | Same as access | JSON format |
| Right to object | N/A | No profiling performed |
| Right to rectification | N/A | No personal data stored by default |

### Cookie Policy

| Cookie | Purpose | Type | Duration |
|---|---|---|---|
| `session_id` | Anonymous session tracking | Functional | Session |
| `format_pref` | Remember preferred format | Functional | 1 year |
| `theme` | Dark/light mode preference | Functional | 1 year |

**No third-party cookies. No advertising cookies. No analytics cookies.**

---

## Data Processing Agreements

Required DPAs with third-party services:

| Service | Data Processed | DPA Status |
|---|---|---|
| Supabase | User emails, feedback, search logs | ✅ Required for Phase 3 |
| Groq | Search queries (text only) | ✅ Check terms of service |
| Qdrant | Meme embeddings (no PII) | ⬜ Not needed (no PII) |
| Cloudflare | Media files (no PII) | ⬜ Not needed (no PII) |
| Vercel | Server logs (masked IPs) | ✅ Built-in DPA |

---

> **Related Documents:**
> - [Security_Overview.md](./Security_Overview.md) · [03_Backend/Middleware.md](../03_Backend/Middleware.md)
