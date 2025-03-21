# Metric Taxonomy

transparency-engine defines a canonical set of Trust & Safety metrics that can be mapped to any regulatory framework. This document describes each metric category and its constituent metrics.

## Categories

| Category | Description |
|----------|-------------|
| `content_moderation` | User-reported and platform-actioned content metrics |
| `government_requests` | Legal orders and requests from authorities |
| `automated_enforcement` | Metrics related to automated detection and action |
| `user_reporting` | User report volumes and resolution times |
| `appeals_and_complaints` | Appeal and complaint handling outcomes |
| `account_integrity` | Account-level enforcement (suspensions, reinstatements) |
| `staffing` | Trust & Safety headcount and resource allocation |
| `reach` | Platform reach and active user metrics |

## Content Moderation

| Metric ID | Name | Type | Unit |
|-----------|------|------|------|
| `cm_items_reported` | Content items reported by users | integer | count |
| `cm_items_actioned` | Content items actioned | integer | count |
| `cm_removal_rate` | Content removal rate | percentage | percent |
| `cm_median_action_time` | Median time to action | float | hours |
| `cm_proactive_detection_rate` | Proactive detection rate | percentage | percent |

## Government Requests

| Metric ID | Name | Type | Unit |
|-----------|------|------|------|
| `gov_orders_received` | Government orders received | integer | count |
| `gov_compliance_rate` | Government order compliance rate | percentage | percent |
| `gov_median_response_time` | Median response time to orders | float | hours |

## Automated Enforcement

| Metric ID | Name | Type | Unit |
|-----------|------|------|------|
| `auto_items_flagged` | Items flagged by automated systems | integer | count |
| `auto_items_actioned` | Items actioned by automated systems | integer | count |
| `auto_false_positive_rate` | Automated false positive rate | percentage | percent |
| `auto_overturn_rate` | Automated action overturn rate | percentage | percent |

## User Reporting

| Metric ID | Name | Type | Unit |
|-----------|------|------|------|
| `ur_report_volume` | User report volume | integer | count |
| `ur_median_resolution_time` | Median report resolution time | float | hours |

## Appeals and Complaints

| Metric ID | Name | Type | Unit |
|-----------|------|------|------|
| `ac_appeals_received` | Appeals received | integer | count |
| `ac_appeal_overturn_rate` | Appeal overturn rate | percentage | percent |
| `ac_complaints_received` | Complaints received | integer | count |

## Account Integrity

| Metric ID | Name | Type | Unit |
|-----------|------|------|------|
| `ai_accounts_suspended` | Accounts suspended | integer | count |
| `ai_accounts_reinstated` | Accounts reinstated | integer | count |

## Staffing

| Metric ID | Name | Type | Unit |
|-----------|------|------|------|
| `staff_moderation_fte` | Content moderation FTE | float | fte |

## Reach

| Metric ID | Name | Type | Unit |
|-----------|------|------|------|
| `reach_mau` | Monthly active users | integer | count |

## Cross-Framework Mapping

The same underlying data often maps to different metric names across regulators. For example:

| Canonical | DSA | OSA |
|-----------|-----|-----|
| `cm_items_reported` | `notices_received` | `illegal_content_reports_received` |
| `cm_items_actioned` | `notices_actioned` | `illegal_content_actioned` |
| `ac_appeals_received` | -- | `appeals_received` |
| `gov_orders_received` | `content_moderation_orders_received` | -- |

Use `FrameworkMetricMapper` to translate between canonical and framework-specific identifiers:

```python
from transparency_engine.metrics.mapping import FrameworkMetricMapper

mapper = FrameworkMetricMapper("dsa")
canonical = mapper.to_canonical("notices_received")  # "cm_items_reported"
```

## Versioning

Metric definitions evolve as regulations are updated. The `MetricVersionRegistry` tracks which definition was in effect for each reporting period, enabling backwards-compatible reporting and restatement detection.
