# DSA Transparency Reporting Guide

This guide covers how to use transparency-engine to produce reports compliant with the EU Digital Services Act (Regulation (EU) 2022/2065).

## Applicable Articles

transparency-engine implements reporting structures for:

- **Article 15** -- Transparency reporting obligations for all intermediary service providers
- **Article 24** -- Additional obligations for online platforms (automated means, recommender systems)
- **Article 42** -- Additional obligations for VLOPs and VLOSEs (very large online platforms and search engines)

## Reporting Cadence

DSA requires transparency reports to be published **at least once a year** for standard providers, and **every six months** for VLOPs/VLOSEs. transparency-engine defaults to semi-annual (H1/H2) periods.

## Required Metrics

### Article 15(1)(a) -- Orders from authorities

| Metric ID | Description |
|-----------|-------------|
| `content_moderation_orders_received` | Orders received from Member State authorities under Art. 9 |
| `content_moderation_orders_median_response_time` | Median time to inform authority of action taken |

Breakdown: by Member State, by order type.

### Article 15(1)(b) -- Notice-and-action

| Metric ID | Description |
|-----------|-------------|
| `notices_received` | Notices submitted via Art. 16 mechanisms |
| `notices_actioned` | Notices resulting in removal, disabling, or demotion |
| `notices_median_response_time` | Median time from notice to action |

Breakdown: by content type, by submission channel.

### Article 15(1)(c) -- Complaints

| Metric ID | Description |
|-----------|-------------|
| `complaints_received` | Complaints under Art. 20 |
| `complaints_reversed` | Decisions reversed following complaint |
| `complaints_median_resolution_time` | Median resolution time |

### Article 15(1)(d) -- Out-of-court settlement

| Metric ID | Description |
|-----------|-------------|
| `out_of_court_disputes` | Disputes referred to Art. 21 bodies |
| `out_of_court_outcomes_upheld` | Outcomes in favour of platform |

### Article 15(1)(e) -- Suspensions and automated means

| Metric ID | Description |
|-----------|-------------|
| `account_suspensions_tos` | Accounts suspended for ToS violations |
| `account_suspensions_manifestly_illegal` | Accounts suspended for manifestly illegal content |
| `automated_detection_items` | Items identified by automated means |
| `content_removals_own_initiative` | Content removed proactively |

### Article 15(1)(f) -- Resources

| Metric ID | Description |
|-----------|-------------|
| `content_moderation_staff_fte` | FTE dedicated to content moderation |

## Data Format

Prepare a CSV with at minimum these columns:

```csv
metric_id,period,value
notices_received,2024-H1,284750
notices_actioned,2024-H1,213562
```

Optional breakdown columns (`content_type`, `country`, `action_type`) can be included for granular reporting.

## Generating a Report

```bash
transparency-engine init --framework dsa --platform-name "My Platform"
transparency-engine ingest --data data/metrics.csv --period 2024-H1
transparency-engine validate --framework dsa --period 2024-H1 --data data/metrics.csv
transparency-engine generate --framework dsa --period 2024-H1 --data data/metrics.csv --format html
```

## Validation Rules

The validator checks:

1. All required metrics are present
2. No negative values in count metrics
3. Subset metrics don't exceed parent totals (e.g., complaints_reversed <= complaints_received)
4. Percentage metrics fall within 0-100
5. Large period-over-period swings are flagged for restatement review
