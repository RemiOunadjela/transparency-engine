"""Tests for metric taxonomy, mapping, and versioning."""

from datetime import date

from transparency_engine.metrics.mapping import FrameworkMetricMapper
from transparency_engine.metrics.taxonomy import METRIC_TAXONOMY, MetricCategory
from transparency_engine.metrics.versioning import (
    MetricVersion,
    MetricVersionRegistry,
    get_default_registry,
)


class TestTaxonomy:
    def test_taxonomy_not_empty(self):
        assert len(METRIC_TAXONOMY) > 10

    def test_all_categories_represented(self):
        categories = {d.category for d in METRIC_TAXONOMY.values()}
        assert MetricCategory.CONTENT_MODERATION in categories
        assert MetricCategory.GOVERNMENT_REQUESTS in categories
        assert MetricCategory.AUTOMATED_ENFORCEMENT in categories
        assert MetricCategory.USER_REPORTING in categories

    def test_metric_definition_fields(self):
        defn = METRIC_TAXONOMY["cm_items_reported"]
        assert defn.name == "Content items reported by users"
        assert defn.category == MetricCategory.CONTENT_MODERATION
        assert defn.data_type == "integer"
        assert "content_type" in defn.breakdown_dimensions

    def test_supports_breakdown(self):
        defn = METRIC_TAXONOMY["cm_items_reported"]
        assert defn.supports_breakdown("content_type") is True
        assert defn.supports_breakdown("nonexistent") is False


class TestMapping:
    def test_dsa_to_canonical(self):
        mapper = FrameworkMetricMapper("dsa")
        assert mapper.to_canonical("notices_received") == "cm_items_reported"
        assert mapper.to_canonical("content_moderation_orders_received") == "gov_orders_received"

    def test_dsa_from_canonical(self):
        mapper = FrameworkMetricMapper("dsa")
        assert mapper.from_canonical("cm_items_reported") == "notices_received"

    def test_osa_mapping(self):
        mapper = FrameworkMetricMapper("osa")
        assert mapper.to_canonical("illegal_content_reports_received") == "cm_items_reported"
        assert mapper.to_canonical("appeals_received") == "ac_appeals_received"

    def test_unknown_metric_returns_none(self):
        mapper = FrameworkMetricMapper("dsa")
        assert mapper.to_canonical("totally_fake_metric") is None

    def test_unknown_framework_empty(self):
        mapper = FrameworkMetricMapper("nonexistent")
        assert mapper.all_mappings() == []

    def test_all_mappings_returns_list(self):
        mapper = FrameworkMetricMapper("dsa")
        mappings = mapper.all_mappings()
        assert len(mappings) > 5


class TestVersioning:
    def test_default_registry_has_entries(self):
        registry = get_default_registry()
        assert len(registry.list_metrics()) > 0

    def test_get_version(self):
        registry = get_default_registry()
        v = registry.get_version("cm_items_actioned", date(2024, 3, 1))
        assert v is not None
        assert v.version == "1.0"

    def test_get_version_after_update(self):
        registry = get_default_registry()
        v = registry.get_version("cm_items_actioned", date(2024, 9, 1))
        assert v is not None
        assert v.version == "1.1"

    def test_is_compatible_stable_period(self):
        registry = get_default_registry()
        assert registry.is_compatible("cm_items_reported", date(2024, 1, 1), date(2024, 6, 30))

    def test_history(self):
        registry = get_default_registry()
        hist = registry.history("cm_items_actioned")
        assert len(hist) == 2
        assert hist[0].version == "1.0"
        assert hist[1].version == "1.1"

    def test_register_custom_version(self):
        registry = MetricVersionRegistry()
        v = MetricVersion(
            metric_id="custom_metric",
            version="1.0",
            effective_from=date(2024, 1, 1),
            changes="Initial.",
        )
        registry.register(v)
        assert "custom_metric" in registry.list_metrics()
        assert registry.get_version("custom_metric", date(2024, 6, 1)) == v
