# Call Masking System — Build Roadmap

> **Stack:** Python · Streamlit · Redis · Exotel  
> **Use case:** Emergency dispatch — proxy number assigned when a paramedic is assigned to a case

---

## What Is Call Masking?

Call masking (also called number masking or proxy calling) is a privacy feature where neither the patient nor the paramedic sees each other's real phone numbers. Instead, both parties call a temporary virtual number that acts as a bridge.

### How It Works

1. Case is created → paramedic is assigned → platform generates a temporary proxy number pair
2. Patient calls the proxy number → the platform's telephony system intercepts it
3. System bridges the call → connects to the paramedic's real number
4. Neither party sees the other's real number — the proxy number expires when the case is closed

---

## Technical Architecture

### Virtual Number Pool
The platform maintains a pool of virtual phone numbers. When a paramedic is assigned, the system leases a number pair tied to that session.

### Telephony Middleware
Incoming calls to proxy numbers are intercepted via SIP (Session Initiation Protocol) or PSTN routing rules, then forwarded to the real destination number.

### Session Management
Each proxy-to-real-number mapping is stored in Redis with a TTL (time-to-live) that expires the mapping once the case is closed or the patient is delivered to care.

### Call Recording & Webhooks
Exotel optionally records calls for dispute resolution. A webhook fires on call completion, delivering call status and the recording URL to your server.

---

## System Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| When to assign proxy | When paramedic is assigned | Not at case creation (wasteful), not on call tap (latency) |
| Backend language | Python | Team preference |
| UI framework | Streamlit | Simple demo interface |
| Telephony provider | Exotel | Dominant in India, used by Zomato/Swiggy/Rapido |
| Session store | Redis | Fast in-memory lookup, native TTL support |
| Extra features | Call recording + analytics logging | Audit trail and operational visibility |

---

## Build Roadmap

### Step 1 — Exotel Mock + Proxy Assignment

**Goal:** Get the core flow working locally without real Exotel credentials.

- Python module that mimics Exotel's API responses
- `Case` and `Paramedic` data models
- Logic that assigns a proxy number the moment a paramedic is assigned to a case
- Streamlit UI to trigger the flow and see the proxy assignment happen live

**What you'll see working:** Assign a paramedic → proxy number appears in the UI instantly.

---

### Step 2 — Redis Session Store

**Goal:** Persist the proxy ↔ real number mapping with automatic expiry.

- Connect to Redis (local or cloud)
- Store `proxy_number → real_number` mapping with a TTL
- Expire the mapping on case close or cancellation
- Streamlit UI showing live session state from Redis

**What you'll see working:** Close a case → proxy mapping disappears from Redis automatically.

---

### Step 3 — Real Exotel API Integration

**Goal:** Replace the mock with actual Exotel calls.

- Lease real virtual numbers from Exotel's number pool
- Call Exotel's connect API to bridge the two legs via SIP
- Handle inbound call routing via Exotel's webhook
- Graceful fallback if Exotel API call fails

**What you'll see working:** A real call placed to the proxy number gets bridged to the paramedic's actual phone.

---

### Step 4 — Call Recording + Webhook Handler

**Goal:** Capture call outcomes and store recordings for audit.

- Expose a `/webhook` endpoint to receive Exotel post-call events
- Parse call status (`completed`, `failed`, `busy`, `no-answer`)
- Store recording URL in your database
- Handle consent disclosure (IVR message before call connects)

**What you'll see working:** After a call ends, the recording URL and call status appear in your database automatically.

---

### Step 5 — Analytics Dashboard (Streamlit)

**Goal:** Operational visibility into all calls across cases.

- Live call log table (case ID, paramedic, duration, status)
- Connection rate metric (calls answered vs. total)
- Recording playback links
- Case timeline view (assigned → called → closed)
- Filter by date range, status, or paramedic

**What you'll see working:** A full Streamlit dashboard showing call history, metrics, and recordings.

---

## Flow Diagram (Reference)

```
Order Created (Case opened)
        │
        ▼
Paramedic Assigned ──────────────────────────────────────────────┐
        │                                                         │
        ▼                                                         ▼
Exotel API called                                          Redis stores
(lease proxy number)                                  proxy ↔ real mapping
                                                        (with TTL)
        │
        │  ◄── Call Happens ────────────────────────────────────────────────
        │                                                         │
        ▼                                                         │
Patient calls proxy number                               Lookup in Redis
        │
        ▼
Exotel call bridge
(connects both legs via SIP)
        │
        ├──► Paramedic receives call
        │    (sees proxy caller ID, not patient's real number)
        │
        ▼
Webhook fires to your server
(call status, recording URL)
        │
        ▼
Case closed → Expire proxy mapping
```

---

## Comparison: Basic Integration vs. Production Scale

| Feature | This Build | Swiggy / Zomato Scale |
|---|---|---|
| Core mechanism | Same | Same |
| Number assigned | When paramedic assigned | At order creation |
| Provider | Exotel only | Exotel + fallback providers |
| Orchestration | Direct API call | Internal telephony service |
| IVR / fallback messages | Optional | Yes |
| Analytics | DB logging | Full data warehouse pipeline |

---

## Next Step

Start with **Step 1** — the Exotel mock and proxy assignment logic in Python + Streamlit. Each step is runnable on its own before moving to the next.
