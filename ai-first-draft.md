---
lab3_first_draft:
  source: ai
  tool: "Claude Sonnet 4.6, claude.ai, 11 October 2026"
  ladder: [0.005, 0.01, 0.025, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 2.5, 5.0, 10.0]
  verdict: refuted
  evidence: {p99_seconds: 0.1984, bucket: [0.1, 0.2], relative_width: 0.504}
lab3_flawed_ladder:
  verdict: refuted
  evidence: {p99_seconds: 0.1984, bucket: [0.04, 0.5], relative_width: 2.319}
---
<!-- ai-generated: 40% - assistant gave ladder and alert rule, verdicts written by student -->

# The assistant first draft, and two verdicts

## Prompt

I am building a service desk API in Python with FastAPI. The endpoint GET /kb/search proxies requests to an upstream knowledge base index. I need histogram bucket boundaries for measuring the latency of this endpoint, and an alert rule for an SLO. The p99 latency is around 150-200 ms. Please suggest histogram bucket boundaries in seconds and a Prometheus alert rule.

## Answer

Here are histogram bucket boundaries in seconds for your GET /kb/search endpoint with p99 around 150-200 ms. Suggested boundaries: 0.005, 0.01, 0.025, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 2.5, 5.0, 10.0. For the Prometheus alert rule, use a single-window rule: alert when histogram_quantile(0.99) over the last 5 minutes exceeds 0.5 seconds, with for 5m and severity P2.

## Verdict on the draft ladder

The p99 measured by the checker is 0.1984 s. The draft ladder places this in the bucket (0.1, 0.2], which has width 0.1 s. The relative width is 0.1 divided by 0.1984 which equals 0.504, meaning 50.4 percent of the p99. Since 50.4 percent is well above the 20 percent threshold, the bucket is too wide to resolve the p99 with the required precision. Verdict: refuted.

## The draft alert rule

The assistant suggested a single-window rule on the latency p99. It has no short window, so it would fail the reset probe: after a burst of slow requests ends, the alert would keep firing for up to half the window. In my own alerts.yml I use a multiwindow rule with both a long and a short window applied to the availability SLI, which is more stable and directly tied to the error budget.

## Verdict on the instructor flawed ladder

The flawed ladder from buckets-flawed.example.yml has boundaries at 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0. The p99 of 0.1984 s falls in the bucket (0.04, 0.5], which has width 0.46 s. The relative width is 0.46 divided by 0.1984 which equals 2.319, meaning 231.9 percent of the p99. This is far above the 20 percent threshold so the flawed ladder cannot resolve the p99 with acceptable precision. Verdict: refuted.