# 001 — Open-source only for production weights

**Status:** accepted
**Date:** 2026-05-25

## Context

We're building Pakistan's commercial speech AI stack. Two paths:
- (A) Wrap third-party APIs (OpenAI Whisper API, ElevenLabs, Google Cloud STT)
- (B) Own the model weights via open-source fine-tuning

Path A ships in days but creates permanent dependency on foreign vendors with unit economics outside our control. Path B requires more engineering but creates a defensible asset.

## Decision

Production weights for Suno will come from Apache-2.0 / MIT licensed base models fine-tuned on Pakistani-curated data. We do not ship third-party APIs as products.

## Rationale

1. **Sovereignty** — "Pakistan's speech AI" with rented weights is a marketing claim, not a technical one.
2. **Unit economics** — owning the weights collapses per-minute cost to compute. A wrapped API at $0.006/minute has no path to compete with regional incumbents.
3. **Customization** — fine-tuning for Pakistani phonetics + Urdu-English code-switching is impossible against a closed API.
4. **Compliance** — Pakistani financial / government customers will eventually require on-prem deployment, which closed APIs don't allow.

## Consequences

- Slower time to market (months vs. days for path A).
- Compute and storage cost falls on us (mitigated by 16 GB M5 Pro + autonomous loop, see [hardware.md](../hardware.md)).
- Eval discipline is mandatory — we can't lean on a vendor's reported quality numbers.
- Meta's MMS / SeamlessM4T are CC-BY-NC → **benchmark-only**, never shipped.

## Alternatives considered

- **Hybrid** (start with API, fine-tune in parallel): rejected because it splits engineering focus and trains us to depend on the API.
- **Pure API wrap MVP**: rejected because the user is technical enough to value the long game.
