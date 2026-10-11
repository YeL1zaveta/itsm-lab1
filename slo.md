---
lab3_slo:
  service: svcdesk
  route: /kb/search
  window: 28d
  slis:
    availability:
      objective: 0.99
      good: 'sum(rate(http_server_request_duration_seconds_count{job="svcdesk", http_route="/kb/search", http_response_status_code=~"2.."}[5m]))'
      valid: 'sum(rate(http_server_request_duration_seconds_count{job="svcdesk", http_route="/kb/search"}[5m]))'
      error_budget: {fraction: 0.01, minutes: 403.2}
    latency:
      objective: 0.95
      threshold_seconds: 0.165
      good: 'sum(rate(http_server_request_duration_seconds_bucket{job="svcdesk", http_route="/kb/search", le="0.165"}[5m]))'
      valid: 'sum(rate(http_server_request_duration_seconds_count{job="svcdesk", http_route="/kb/search"}[5m]))'
      error_budget: {fraction: 0.05, minutes: 2016.0}
  alerts:
    - {alert: KbSearchAvailabilityFastBurn, sli: availability, burn_rate: 14.4, long_window: 1h, short_window: 5m}
    - {alert: KbSearchAvailabilitySlowBurn, sli: availability, burn_rate: 6.0, long_window: 6h, short_window: 30m}
---
<!-- ai-generated: 30% - structure from template, numbers and prose written by student -->

## Availability

The availability SLI counts HTTP 2xx responses as good and all responses as valid for GET /kb/search. The objective is 99%, giving an error budget of 1% of 28 days, which is 403.2 minutes. kb-index itself has its own failure modes that svcdesk cannot fix: when kb-index returns 503, svcdesk returns 502, which counts as a bad request. This means the availability objective must leave room for kb-index outages.

## Latency

The latency SLI counts requests at or below 0.165 s as good. The p99 measured by the checker was 0.1656 s, and 0.165 is a boundary in the ladder that sits just below the p99, giving a threshold in the band around the measured p99. The objective is 95%, meaning 5% of requests may exceed 0.165 s. The error budget is 5% of 28 days, which is 2016 minutes. This objective accommodates the slow mode of kb-index which occasionally adds latency.

## Alerts

| alert | SLI | burn rate | long / short window | budget spent when it fires | severity |
|---|---|---|---|---|---|
| KbSearchAvailabilityFastBurn | availability | 14.4 | 1h / 5m | 2% in 1h | P1 page |
| KbSearchAvailabilitySlowBurn | availability | 6.0 | 6h / 30m | 5% in 6h | P2 chat |

The fast burn alert pages a person because at 14.4x burn rate the entire error budget would be gone in 2 hours. Waking someone is justified. The slow burn alert goes to chat because at 6x burn rate there are still many hours before the budget is exhausted, so it can wait until morning.

## Buckets

The ladder has fine-grained boundaries around the measured p99 of 0.1656 s: 0.15, 0.16, 0.165, 0.17, 0.175, 0.18, 0.185, 0.19, 0.195, 0.20. The p99 falls in the bucket (0.165, 0.17], which has width 0.005 s, a relative width of 3% of the p99. This resolves a band from 0.165 to 0.17 around the p99, which is well within the required 10% band. The remaining boundaries cover the full range from 5ms to 5s for other routes.
