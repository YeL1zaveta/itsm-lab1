---
svcdesk_decisions:
  C1: wallclock
  C2: immutable
  C3: vip
---
<!-- ai-generated: 20% - structure from template, content written by student -->

# Decisions

## C1 - SLA clock for P1

**Decision:** P1 tickets use a wall-clock target, running 24 hours a day, 7 days a week without pausing outside business hours.

**Rejected alternative:** Using the business-hours clock for P1, which would pause the SLA timer overnight and on weekends.

**Reason:** P1 means the entire organisation is affected and work has stopped. Waiting until Monday morning to count time is unacceptable for the most critical incidents.

**Service owner:** The CTO or Head of IT Operations owns this decision because it directly affects contractual SLA commitments to the business.

**Customer outcome:** Reporters of critical incidents receive a guaranteed response within 15 minutes at any time of day or night, including weekends and holidays.

## C2 - Closed tickets and reopening

**Decision:** Closed tickets are immutable. If the fix did not work, the reporter must open a new ticket referencing the closed one via related_to.

**Rejected alternative:** Allowing reporters to reopen closed tickets within a 7-day window after closure.

**Reason:** Immutability of closed tickets ensures the integrity of audit trails and historical reporting. Each problem has its own traceable lifecycle.

**Service owner:** The Service Desk Manager owns this decision as it defines the core ticket lifecycle process used in all reporting.

**Customer outcome:** The service history remains accurate and reliable. Every distinct problem is tracked with its own identifier, making reports trustworthy.

## C3 - VIP reporters and the priority matrix

**Decision:** Tickets from VIP reporters are always raised to at least P2, even if the impact and urgency matrix would give P3 or P4.

**Rejected alternative:** Using only the priority matrix for all reporters, ignoring the VIP flag for priority calculation.

**Reason:** Executive and key-account issues must be immediately visible to the desk regardless of their technical impact score.

**Service owner:** The Head of IT approves the VIP escalation policy as it affects resource allocation and executive satisfaction.

**Customer outcome:** VIP reporters receive faster acknowledgement and resolution, ensuring critical business relationships are protected.