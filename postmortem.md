---
lab4_postmortem:
  ticket: "3ba75e92-1b55-483b-a69e-6097c02b182c"
  detecting_alert: ShopCheckoutSlow
  onset: 2026-10-12T05:01:00Z
  detection: 2026-10-12T05:06:19Z
  acknowledgement: 2026-10-12T05:06:56Z
  recovery: 2026-10-12T05:08:19Z
  mttd_seconds: 319
  mtta_seconds: 37
  mttr_seconds: 439
  identified_flags: [intlShippingSlowdown, emailMemoryLeak, adFailure]
---
<!-- ai-generated: 60% - an assistant drafted the prose from my query results, I checked every number on the recording -->

# Postmortem: Shop checkout became slow for about seven minutes

## Date

The incident happened on 2026-10-12 (UTC); this postmortem was written on 2026-10-25.

## Authors

Written by yel1zaveta, acting as the on-call engineer who analysed recording lab4-rec-1.

## Status

Complete, action items in progress; the shop recovered at 05:08:19Z and no fault remains.

## Summary

Checkout latency rose from about 50 ms to about 9 seconds (p99) for roughly seven minutes, and the ShopCheckoutSlow alert paged the on-call.

## Impact

Checkout p99 went from 49.6 ms at 04:56:00Z to 9050 ms at 05:06:00Z, measured with histogram_quantile(0.99, sum by (le, service_name) (rate(traces_span_metrics_duration_milliseconds_bucket{span_kind="SPAN_KIND_SERVER"}[5m]))). Checkout throughput fell from 0.15 to 0.079 requests per second, and ad errors reached 0.012 per second.

## Root Causes

Three faults were active at once. intlShippingSlowdown slowed shipping (p99 5.3 ms to 8100 ms), which made checkout wait for it. emailMemoryLeak degraded email (p99 7.9 ms to 181 ms). adFailure produced errors in ad (about 6 percent of its requests) that reached the frontend.

## Trigger

The faults started at the onset, 05:01:00Z, when the injector's flags took effect; the baseline before it was healthy.

## Resolution

Service recovered at 05:08:19Z, when the detecting alert stopped firing after the faulty flags were switched off in the lecturer's run. On this recording I could not read the flags, so I identified them from symptoms only.

## Detection

ShopCheckoutSlow (p99 of checkout server spans above 2000 ms for 2 minutes) paged at 05:06:19Z, which is an MTTD of 319 seconds; the ticket was acknowledged 37 seconds later.

## Action Items

| Action Item | Type | Owner | Bug |
|---|---|---|---|
| Add an alert on shipping p99 latency so the cause is visible, not only the checkout symptom | prevent | on-call | ITSM-101 |
| Lower the for: duration of ShopCheckoutSlow to shorten MTTD | mitigate | on-call | ITSM-102 |
| Add a runbook step to check feature flags first when checkout is slow | process | on-call | ITSM-103 |

## Lessons Learned

### What went well

The latency alert fired on the symptom users felt and stayed quiet on the healthy baseline.

### What went wrong

The AI investigator blamed product-catalog and payment, whose metrics did not change at all.

### Where we got lucky

Checkout errors stayed at zero, so a rule on errors alone would have missed this incident.

## Timeline

All times UTC on 2026-10-12. 05:00:00 last quiet minute: checkout p99 about 50 ms. 05:01:00 onset. 05:06:00 checkout p99 9050 ms, shipping 8100 ms. 05:06:19 ShopCheckoutSlow detected and paged. 05:06:36 P1 ticket created. 05:06:56 ticket acknowledged. 05:08:19 recovery. AI hypothesis H1 (product-catalog is slow) was tested with histogram_quantile(0.99, sum by (le) (rate(traces_span_metrics_duration_milliseconds_bucket{service_name="product-catalog", span_kind="SPAN_KIND_SERVER"}[5m]))) > 1000 at 05:06:00 and was false, so I did not act on it. H3 (payment failed) was tested the same way on payment errors and was false.

## Supporting information

Supporting data: itsmlab incident 4 output (onset, detection, acknowledgement, recovery), the p99, error and throughput queries above on the served recording, and the ledger ai-rca-eval.json with its transcript ai-rca/transcript.md.

## Problem record

- Incident record: ticket 3ba75e92-1b55-483b-a69e-6097c02b182c, P1, checkout slow, acknowledged at 05:06:56Z.
- Root cause: intlShippingSlowdown made shipping slow, which delayed every checkout, together with emailMemoryLeak and adFailure.
- Known error: a slow shipping dependency stretches checkout latency to seconds while checkout itself shows no errors.
- Workaround: switch the faulty flags off through the injector, which restored service within minutes.