# transparency-engine

[![CI](https://github.com/RemiOunadjela/transparency-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/RemiOunadjela/transparency-engine/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Open-Source Transparency Reporting for Digital Platforms**

A framework for generating regulatory-compliant transparency reports across multiple jurisdictions. Supports the EU Digital Services Act (DSA), UK Online Safety Act (OSA), and custom regulatory frameworks via pluggable templates.

---

## Why transparency-engine?

Having delivered 45+ transparency reports across DSA, OSA, and voluntary disclosure programs, I kept hitting the same problems:

- **Manual, error-prone processes.** Regulatory teams copy-paste metrics between spreadsheets, re-derive the same figures for each jurisdiction, and catch formatting errors at the eleventh hour.
- **No cross-framework consistency.** The same underlying metric -- say, proactive detection rate -- has different names, different aggregation rules, and different reporting periods across the DSA, OSA, and platform-specific voluntary commitments. Keeping them aligned manually is a recipe for restatements.
- **Audit gaps.** When a regulator asks "how did you arrive at this number?", the answer is often a chain of emails and ad-hoc scripts that nobody documented.
- **Siloed tooling.** Every platform builds its own internal pipeline. The regulatory reporting problem is fundamentally the same everywhere, but the tooling is rebuilt from scratch each time.

transparency-engine solves this by providing a single, validated pipeline from raw metrics to publication-ready reports -- with full audit trail, cross-framework metric mapping, and built-in validation rules that catch the kinds of errors regulators actually flag.

## Quick Start

### Installation

```bash
pip install transparency-engine
```

### From raw data to published report in 5 commands

```bash
# 1. Scaffold a new DSA reporting project
transparency-engine init --framework dsa --platform-name "Acme Social"

# 2. Ingest your metrics data
transparency-engine ingest --data data/metrics.csv --period 2024-H1

# 3. Validate against framework requirements
transparency-engine validate --framework dsa --period 2024-H1 --data data/metrics.csv

# 4. Generate the report
transparency-engine generate --framework dsa --period 2024-H1 --data data/metrics.csv --format html

# 5. Compare with the previous period
transparency-engine compare --periods 2024-H1,2023-H2 --data data/metrics.csv
```

### Python API

```python
from transparency_engine.frameworks import get_framework
from transparency_engine.ingestion import load_data
from transparency_engine.config import OutputFormat, PeriodSpec
from transparency_engine.reports import ReportGenerator
from transparency_engine.validation import run_validation

# Load framework and data
framework = get_framework("dsa")
data = load_data("data/metrics.csv")
period = PeriodSpec.parse("2024-H1")

# Validate
results = run_validation(data, framework)
for r in results:
    print(f"[{'PASS' if r.passed else 'FAIL'}] {r.check_name}: {r.message}")

# Generate
generator = ReportGenerator(
    framework=framework,
    period=period,
    data=data,
    platform_name="Acme Social",
)
generator.generate(OutputFormat.HTML, output_path="reports/dsa_2024_h1.html")
```

## Data Format

Prepare a CSV (or JSON/Parquet) with at minimum these columns:

```csv
metric_id,period,value
notices_received,2024-H1,284750
notices_actioned,2024-H1,213562
notices_median_response_time,2024-H1,4.2
complaints_received,2024-H1,47830
```

Optional breakdown columns (`content_type`, `country`, `action_type`) enable granular reporting as required by specific frameworks.

## Architecture

```
                    +-----------------+
                    |   Raw Data      |
                    | CSV/JSON/Parquet|
                    +--------+--------+
                             |
                    +--------v--------+
                    |   Ingestion     |
                    | Load + Validate |
                    +--------+--------+
                             |
               +-------------+-------------+
               |                           |
      +--------v--------+        +--------v--------+
      |   Validation    |        |   Transforms    |
      | Completeness    |        | Aggregation     |
      | Consistency     |        | Period alignment|
      | Bounds checks   |        | Comparison      |
      +--------+--------+        +--------+--------+
               |                           |
               +-------------+-------------+
                             |
                    +--------v--------+
                    |   Framework     |
                    | DSA / OSA /     |
                    | Custom          |
                    +--------+--------+
                             |
                    +--------v--------+
                    | Report Generator|
                    | HTML / MD / PDF |
                    | + Visualizations|
                    +--------+--------+
                             |
                    +--------v--------+
                    |   Audit Trail   |
                    | Full provenance |
                    +-----------------+
```

## Supported Frameworks

| Framework | Jurisdiction | Cadence | Articles / Sections |
|-----------|-------------|---------|---------------------|
| **DSA** (Digital Services Act) | EU | Semi-annual | Art. 15, 24, 42 |
| **OSA** (Online Safety Act) | UK | Annual | OFCOM Transparency Reporting guidance |
| **Custom** | Any | Configurable | User-defined via JSON |

## Metric Taxonomy

transparency-engine defines a canonical metric taxonomy that maps across regulatory frameworks. The same underlying data feeds multiple reports without manual re-derivation.

| Category | Example Metrics |
|----------|----------------|
| Content Moderation | Items reported, items actioned, removal rate, median action time |
| Government Requests | Orders received, compliance rate, response time |
| Automated Enforcement | Items flagged, items actioned, false positive rate, overturn rate |
| User Reporting | Report volume, resolution time |
| Appeals & Complaints | Appeals received, overturn rate, complaints received |
| Account Integrity | Accounts suspended, accounts reinstated |
| Staffing | Content moderation FTE (by language/region) |
| Reach | Monthly active users/recipients |

Cross-framework mapping handles the translation automatically:

```python
from transparency_engine.metrics.mapping import FrameworkMetricMapper

mapper = FrameworkMetricMapper("dsa")
mapper.to_canonical("notices_received")  # -> "cm_items_reported"

mapper = FrameworkMetricMapper("osa")
mapper.to_canonical("illegal_content_reports_received")  # -> "cm_items_reported"
```

## Validation

Pre-publication checks catch common errors before they reach a regulator:

- **Completeness**: all required metrics for the framework are present
- **Negative values**: count metrics should never be negative
- **Consistency**: subset metrics don't exceed their parent totals (e.g., appeals upheld <= appeals received)
- **Percentage bounds**: rate metrics fall within 0-100
- **Historical restatement detection**: flags metrics that swing by more than 50% period-over-period

## Custom Frameworks

Define your own framework in JSON:

```json
{
  "name": "Internal Trust & Safety Review",
  "short_code": "internal",
  "reporting_cadence": "quarterly",
  "metrics": [
    {
      "metric_id": "user_reports_total",
      "name": "Total user reports",
      "description": "All reports submitted via in-app flows.",
      "required": true
    }
  ],
  "sections": [
    {
      "section_id": "overview",
      "title": "Enforcement Overview",
      "description": "High-level enforcement activity.",
      "metrics": ["user_reports_total"],
      "order": 1
    }
  ]
}
```

```python
from transparency_engine.frameworks.custom import CustomFramework

framework = CustomFramework.from_file("my_framework.json")
```

## Development

```bash
git clone https://github.com/RemiOunadjela/transparency-engine.git
cd transparency-engine
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## License

MIT -- see [LICENSE](LICENSE).
