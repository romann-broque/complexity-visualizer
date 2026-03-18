# Coupling Visualization Guide

This guide explains how to use the new coupling metrics in CodeCharta to analyze architectural quality and identify problematic dependencies.

## 🎯 New Coupling Metrics

### 1. **cycleParticipation**
- **What**: Size of the dependency cycle this class belongs to (0 if no cycle)
- **Why**: Classes in cycles are tightly coupled and cannot be modified independently
- **Good**: 0 (no cycle)
- **Bad**: >2 (circular dependencies exist)

### 2. **bidirectionalLinks**
- **What**: Number of classes with mutual dependencies (A→B AND B→A)
- **Why**: Bidirectional dependencies indicate tight coupling even outside formal cycles
- **Good**: 0 (unidirectional dependencies)
- **Bad**: >0 (mutual dependencies)

### 3. **crossPackageDeps**
- **What**: Number of different packages this class depends on
- **Why**: High values indicate boundary violations in Clean Architecture
- **Good Domain**: 0-1 (domain should be isolated)
- **Good Application**: 2-3 (depends on domain + few utilities)
- **Bad**: >5 (too many package dependencies)

### 4. **instability** (Robert C. Martin)
- **What**: `I = fanOut / (fanIn + fanOut)`
- **Why**: Measures architectural stability - stable classes should not change
- **Values**:
  - `I = 0.0`: Maximally stable (many dependents, few dependencies)
  - `I = 0.5`: Balanced
  - `I = 1.0`: Maximally unstable (few dependents, many dependencies)

**Expected by layer (Clean Architecture)**:
- **Domain**: I ≈ 0.0-0.2 (stable, no outgoing dependencies)
- **Application**: I ≈ 0.3-0.5 (moderate)
- **Infrastructure**: I ≈ 0.7-1.0 (unstable, depends on everything)

---

## 🎨 CodeCharta Visualization Strategies

### Strategy 1: Find Cycles (Highest Priority)

**Configuration**:
```
Height: maintenanceBurden
Color: cycleParticipation  ⭐
Area: fanIn
Filter: Show only classes with cycleParticipation > 0
```

**What you'll see**:
- **Purple/Red buildings** = Classes in cycles
- **Larger buildings** = Larger cycles (harder to break)
- **Empty map** = No cycles ✅ (like POSeidon V2 with only 9 small cycles)

**Action**: Prioritize breaking cycles by introducing interfaces or event-driven architecture.

---

### Strategy 2: Validate Clean Architecture

**Configuration**:
```
Height: instability
Color: crossPackageDeps
Area: fanIn
Filter: domain.* only (show only domain layer)
```

**Expected (Good Architecture)**:
- **Domain layer**: Short buildings (I ≈ 0), green color (crossPackageDeps ≈ 0)
- **Application layer**: Medium buildings (I ≈ 0.4), yellow (crossPackageDeps ≈ 2-3)
- **Infrastructure layer**: Tall buildings (I ≈ 0.8), red acceptable (depends on many packages)

**Violations to spot**:
- **Tall buildings in domain** = Domain depends on infrastructure ❌
- **Red domain classes** = Domain depends on many packages ❌
- **Green infrastructure** = Infrastructure is too stable (leaky abstraction) ❌

**POSeidon V2 Results**:
- Domain: I = 0.400 (⚠️ slightly high, should be < 0.2)
- Application: I = 0.476 ✅
- Infrastructure: I = 0.649 ✅

---

### Strategy 3: Detect Bidirectional Coupling

**Configuration**:
```
Height: bidirectionalLinks
Color: maintenanceBurden
Area: fanIn
Filter: Show only classes with bidirectionalLinks > 0
```

**What you'll see**:
- **Tall buildings** = Classes with many mutual dependencies
- **Red color** = High maintenance burden (hard to change)

**Action**: Refactor bidirectional dependencies by:
1. Introducing interfaces (Dependency Inversion)
2. Using events/callbacks
3. Extracting shared abstractions

**POSeidon V2**: 22 classes with bidirectional links out of 2293 (0.96%) ✅

---

### Strategy 4: Compare Projects Side-by-Side

**Well-Decoupled Project (like POSeidon V2)**:
- **Cycles**: Few cycles (9), small size (2-3 classes)
- **Instability**: Proper gradient (Domain low, Infra high)
- **Cross-package**: Most classes depend on < 3 packages
- **Visualization**: Flat, green/yellow landscape

**Tightly-Coupled Monolith**:
- **Cycles**: Many cycles (>50), large size (>10 classes)
- **Instability**: Inverted (Domain high, Infra low)
- **Cross-package**: Most classes depend on >5 packages
- **Visualization**: Tall red/purple towers, dense clustering

---

## 📊 Thresholds Reference

### Green Zone ✅ (Low Coupling)
| Metric | Domain | Application | Infrastructure |
|--------|--------|-------------|----------------|
| cycleParticipation | 0 | 0 | 0 |
| bidirectionalLinks | 0 | 0-1 | 0-1 |
| crossPackageDeps | 0-1 | 2-3 | Any |
| instability | 0.0-0.2 | 0.3-0.5 | 0.7-1.0 |
| maintenanceBurden | <50 | <200 | <300 |

### Yellow Zone ⚠️ (Moderate Coupling)
| Metric | Value | Action |
|--------|-------|--------|
| cycleParticipation | 2-4 | Consider breaking cycle |
| bidirectionalLinks | 2-3 | Introduce interfaces |
| crossPackageDeps | 4-6 | Review package boundaries |
| instability (Domain) | 0.2-0.4 | Check for infra dependencies |
| maintenanceBurden | 200-500 | Plan refactoring |

### Red Zone ❌ (High Coupling)
| Metric | Value | Action |
|--------|-------|--------|
| cycleParticipation | >5 | **Urgent**: Break cycle immediately |
| bidirectionalLinks | >4 | **Refactor**: Decouple classes |
| crossPackageDeps | >7 | **Architecture violation**: Fix boundaries |
| instability (Domain) | >0.5 | **Critical**: Domain depends on infra |
| maintenanceBurden | >1000 | **God class**: Decompose |

---

## 🔧 How to Add/Remove Metrics

The new architecture is fully pluggable. To add a custom metric:

### 1. Create Calculator

```python
# complexity_visualizer/core/metrics/calculators/my_metric.py

from typing import List
from ..base import MetricCalculator, MetricContext

class MyMetricCalculator(MetricCalculator):
    @property
    def name(self) -> str:
        return "myMetric"
    
    @property
    def description(self) -> str:
        return "Description of my metric"
    
    def calculate(self, context: MetricContext) -> List[float]:
        # Your calculation logic here
        return [0.0] * context.n_nodes
```

### 2. Register Calculator

```python
# complexity_visualizer/core/metrics/calculators/__init__.py

from . import my_metric  # Import your module

_registry.register(my_metric.MyMetricCalculator)  # Register it
```

### 3. Update Models (Optional)

```python
# complexity_visualizer/core/models.py

@dataclass
class NodeMetrics:
    # ... existing metrics
    myMetric: float = 0.0  # Add your metric
```

### 4. Update Exporters (Optional)

```python
# complexity_visualizer/exporters/codecharta.py

attrs = {
    # ... existing attrs
    "myMetric": metrics.get("myMetric", 0.0),
}

# In attributeTypes:
"myMetric": "absolute",  # or "relative"
```

**That's it!** The metric will be automatically computed in dependency order.

---

## 📈 POSeidon V2 Analysis Example

```bash
# Generate visualization with all new metrics
complexity-viz run /path/to/poseidon-v2-back \
  --include-prefix com.totalenergies.poseidon2

# Results:
📊 2293 classes, 8156 dependencies
🔍 Coupling Metrics:
   - Cycles: 9 (only 24 classes affected - 1%)
   - Bidirectional links: 22 classes (0.96%)
   - High cross-package deps: 517 classes (22.5%)

📐 Instability by Layer:
   - Domain: 0.400 (⚠️ slightly high)
   - Application: 0.476 ✅
   - Infrastructure: 0.649 ✅

✅ Verdict: Well-decoupled architecture with minor improvements needed
```

**Recommendations for POSeidon V2**:
1. ⚠️ **Domain instability is 0.400** - investigate which domain classes depend on infrastructure
2. ✅ Excellent cycle count (only 9 small cycles out of 2293 classes)
3. ✅ Very low bidirectional coupling (22 classes)
4. ⚠️ 22.5% classes have high cross-package deps - review bounded context boundaries

---

## 🎓 Further Reading

- **Robert C. Martin's Metrics**: [Clean Architecture Chapter 14](https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html)
- **Dependency Cycles**: [Acyclic Dependencies Principle](https://en.wikipedia.org/wiki/Acyclic_dependencies_principle)
- **CodeCharta Documentation**: [https://maibornwolff.github.io/codecharta/](https://maibornwolff.github.io/codecharta/)

---

## 🚀 Quick Commands

```bash
# Analyze your project
complexity-viz run /path/to/project --include-prefix com.yourcompany

# Focus on cycles only
# In CodeCharta: Set Color=cycleParticipation, Filter by >0

# Check Clean Architecture compliance
# In CodeCharta: Set Height=instability, Color=crossPackageDeps, Filter by layer

# Find God classes
# In CodeCharta: Set Height=maintenanceBurden, Color=fanIn, Sort by height descending
```
