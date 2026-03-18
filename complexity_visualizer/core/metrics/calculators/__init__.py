"""Auto-register all metric calculators.

Import this module to register all available metrics with the global registry.
This provides a clean plugin-style architecture where metrics can be added
or removed by simply editing this file.
"""

from ..registry import get_registry
from . import coupling, cycles, degrees, maintenance, stability, transitive

_registry = get_registry()

_registry.register(degrees.FanInCalculator)
_registry.register(degrees.FanOutCalculator)
_registry.register(transitive.TransitiveDepsCalculator)

_registry.register(cycles.CycleParticipationCalculator)

_registry.register(coupling.BidirectionalLinksCalculator)
_registry.register(coupling.CrossPackageDepsCalculator)

_registry.register(stability.InstabilityCalculator)

_registry.register(maintenance.MaintenanceBurdenCalculator)
