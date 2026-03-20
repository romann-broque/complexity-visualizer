"""Pluggable metric calculation system.

This package provides a flexible, extensible system for computing
code metrics. Each metric is implemented as an independent calculator
that can be added or removed without affecting other metrics.

Key features:
- Automatic dependency resolution
- Easy to add/remove metrics
- Shared computation context for efficiency
- Plugin-style architecture
"""

from .base import MetricCalculator, MetricContext
from .registry import MetricRegistry, get_registry

__all__ = ["MetricCalculator", "MetricContext", "MetricRegistry", "get_registry"]
