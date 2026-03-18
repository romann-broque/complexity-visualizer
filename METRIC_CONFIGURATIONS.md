# CodeCharta Metric Configurations

This guide provides ready-to-use metric configurations for CodeCharta to identify specific architectural problems.

---

## 🎯 Quick Reference: Problem Detection Configurations

| Problem | Height | Color | Area | Filter |
|---------|--------|-------|------|--------|
| **Cycles** | cycleParticipation | maintenanceBurden | fanIn | cycleParticipation > 0 |
| **God Classes** | maintenanceBurden | fanIn | transitiveDeps | maintenanceBurden > 500 |
| **Tight Coupling** | bidirectionalLinks | crossPackageDeps | fanIn | bidirectionalLinks > 0 |
| **Architecture Violations** | instability | crossPackageDeps | fanIn | Filter by layer |
| **Breaking Change Risk** | fanIn | maintenanceBurden | transitiveDeps | fanIn > 10 |
| **Dependency Hell** | transitiveDeps | fanOut | fanIn | transitiveDeps > 50 |
| **Hotspots** | maintenanceBurden | cycleParticipation | fanIn | maintenanceBurden > 200 |

---

## 📋 Detailed Configurations

### 1. 🔴 Find Dependency Cycles (Critical Priority)

**Problem**: Classes in cycles cannot be modified independently and prevent refactoring.

**Configuration**:
```yaml
Height: cycleParticipation
Color: maintenanceBurden
Area: fanIn
Filter: cycleParticipation > 0
```

**What you see**:
- **Tall buildings** = Large cycles (more classes stuck together)
- **Red color** = High maintenance burden (hard to change)
- **Large area** = Many dependents (breaking change risk)

**Interpretation**:
- ✅ **No buildings** = No cycles detected (excellent!)
- ⚠️ **Small buildings (2-3)** = Small cycles, manageable
- ❌ **Tall buildings (>5)** = Large cycles, urgent refactoring needed

**Action Priority**:
1. Start with tallest buildings (largest cycles)
2. Look for entry points to break the cycle
3. Introduce interfaces or event-driven patterns

**Example Results**:
- **POSeidon V2**: 9 small cycles, 24 classes total (1% of codebase) ✅
- **Typical monolith**: 50+ cycles, 500+ classes (20% of codebase) ❌

---

### 2. 👹 Detect God Classes

**Problem**: Classes with too many responsibilities, dependencies, and dependents.

**Configuration**:
```yaml
Height: maintenanceBurden
Color: fanIn
Area: transitiveDeps
Filter: maintenanceBurden > 500
Sort: Height descending
```

**What you see**:
- **Tallest buildings** = Hardest classes to change
- **Red color** = Many dependents (breaking change risk)
- **Large area** = Wide blast radius (many transitive dependencies)

**Interpretation**:
| Height | Color | Area | Diagnosis |
|--------|-------|------|-----------|
| >1000 | >20 | >50 | **God Class** - Urgent decomposition |
| 500-1000 | 10-20 | 30-50 | **Fat Class** - Plan refactoring |
| 200-500 | 5-10 | 10-30 | **Complex Class** - Monitor |
| <200 | <5 | <10 | **Healthy** ✅ |

**Action Priority**:
1. **Extract services**: Identify distinct responsibilities
2. **Introduce interfaces**: Reduce fanIn impact
3. **Break dependencies**: Reduce transitiveDeps

**Typical God Classes**:
- `ApplicationContext`
- `ServiceManager`
- `Utils` / `Helper` classes
- Legacy `Facade` classes

---

### 3. 🔗 Identify Tight Coupling

**Problem**: Bidirectional dependencies create tangled code that's hard to test and modify.

**Configuration**:
```yaml
Height: bidirectionalLinks
Color: crossPackageDeps
Area: fanIn
Filter: bidirectionalLinks > 0
```

**What you see**:
- **Tall buildings** = Many mutual dependencies (A↔B, C↔D, etc.)
- **Red color** = Crosses many package boundaries
- **Large area** = Widely used despite tight coupling

**Interpretation**:
| Height | Color | Diagnosis | Action |
|--------|-------|-----------|--------|
| >5 | >5 | **Critical** | Break cycles immediately |
| 3-5 | 3-5 | **Warning** | Introduce interfaces |
| 1-2 | 1-2 | **Minor** | Document and monitor |

**Refactoring Strategies**:
1. **Dependency Inversion**: Create interfaces
   ```java
   // Before: A → B, B → A
   // After: A → IB, B implements IB
   ```
2. **Event-Driven**: Replace method calls with events
3. **Extract Common Logic**: Create shared abstractions

**POSeidon V2 Result**: 22 classes with bidirectional links (0.96%) ✅

---

### 4. 🏗️ Validate Clean Architecture (Layer Violations)

**Problem**: Domain layer depends on infrastructure (violates dependency rule).

#### Configuration A: Domain Layer Only
```yaml
Height: instability
Color: crossPackageDeps
Area: fanIn
Filter: package contains "domain"
```

**Expected (Good Architecture)**:
- **Short buildings** (I < 0.2) = Domain is stable
- **Green color** (crossPackageDeps < 2) = Domain isolated
- **Any area** = fanIn doesn't matter

**Violations**:
- ❌ **Tall buildings** (I > 0.3) = Domain depends on other layers
- ❌ **Red color** (crossPackageDeps > 3) = Domain couples to many packages

#### Configuration B: All Layers Gradient
```yaml
Height: instability
Color: Layer (manual coloring)
Area: fanIn
Filter: none
```

**Expected Gradient**:
```
Domain (I ≈ 0.0-0.2)          ← Stable, no outgoing deps
   ↓
Application (I ≈ 0.3-0.5)     ← Moderate
   ↓
Infrastructure (I ≈ 0.7-1.0)  ← Unstable, many deps
```

**POSeidon V2 Results**:
- Domain: 0.400 (⚠️ slightly high, should be < 0.2)
- Application: 0.476 ✅
- Infrastructure: 0.649 ✅

**Action if violated**:
1. Find domain classes with high instability
2. Check what infrastructure they depend on
3. Introduce ports (interfaces) in application layer
4. Implement adapters in infrastructure

---

### 5. 💥 Breaking Change Risk (High Fan-In)

**Problem**: Classes with many dependents are risky to change (breaking changes).

**Configuration**:
```yaml
Height: fanIn
Color: maintenanceBurden
Area: transitiveDeps
Filter: fanIn > 10
```

**What you see**:
- **Tallest buildings** = Most depended-upon classes
- **Red color** = High change impact
- **Large area** = Wide blast radius

**Interpretation**:
| Height | Risk Level | Action |
|--------|-----------|--------|
| >30 | **Critical** | Public API - versioning required |
| 20-30 | **High** | Major refactoring needs planning |
| 10-20 | **Moderate** | Document changes carefully |
| <10 | **Low** | Normal development ✅ |

**Categories**:
1. **Good high fan-in**: Stable utility classes (e.g., `StringUtils`)
   - Characteristics: Low instability (I ≈ 0), low transitiveDeps
2. **Bad high fan-in**: God classes or central singletons
   - Characteristics: High instability (I > 0.3), high transitiveDeps

**Action**:
- **If utility class**: Keep stable, version API carefully
- **If god class**: Decompose into smaller services

---

### 6. 🕸️ Dependency Hell (Deep Transitive Dependencies)

**Problem**: Changes cascade through many layers (long dependency chains).

**Configuration**:
```yaml
Height: transitiveDeps
Color: fanOut
Area: fanIn
Filter: transitiveDeps > 50
```

**What you see**:
- **Tallest buildings** = Longest dependency chains
- **Red color** = Many direct dependencies (fanOut)
- **Large area** = Also widely depended upon (fanIn)

**Interpretation**:
| Height | Color | Area | Diagnosis |
|--------|-------|------|-----------|
| >100 | >10 | >10 | **Critical** - Dependency spider |
| 50-100 | 5-10 | 5-10 | **Warning** - Deep chains |
| 20-50 | <5 | <5 | **Normal** - Orchestrator pattern ✅ |

**Action**:
1. **Visualize dependency tree**: Trace path to understand depth
2. **Introduce layers**: Break long chains with abstractions
3. **Lazy loading**: Don't transitively pull everything

**Typical Culprits**:
- Root controllers that import entire application
- Service facades that aggregate many sub-services
- Legacy bootstrap classes

---

### 7. 🔥 Overall Hotspots (Combined Risk)

**Problem**: Classes that score badly on multiple metrics.

**Configuration**:
```yaml
Height: maintenanceBurden
Color: cycleParticipation
Area: fanIn
Filter: maintenanceBurden > 200
Sort: Height descending
```

**What you see**:
- **Tallest buildings** = Hardest to maintain
- **Purple/Red color** = In cycles (double trouble)
- **Large area** = Widely used (can't easily delete)

**Risk Matrix**:
| maintenanceBurden | cycleParticipation | Priority |
|-------------------|-------------------|----------|
| >1000 | >0 | 🔥 **URGENT** - Top priority |
| >1000 | 0 | ❌ **HIGH** - Plan soon |
| 500-1000 | >0 | ⚠️ **MEDIUM** - Monitor |
| 200-500 | 0 | 💡 **LOW** - Document |

**Triage Strategy**:
1. **Week 1**: Break cycles for highest maintenanceBurden classes
2. **Week 2-3**: Decompose god classes (maintenanceBurden > 1000)
3. **Month 2**: Reduce bidirectional coupling
4. **Ongoing**: Monitor instability violations

---

## 🎨 Advanced Configurations

### 8. Package Coupling Analysis

**Configuration**:
```yaml
Height: crossPackageDeps
Color: instability
Area: fanOut
Filter: crossPackageDeps > 5
Grouping: By package
```

**Use Case**: Detect bounded context violations in DDD/microservices.

**Expected**:
- **Domain packages**: Short buildings (crossPackageDeps < 2)
- **Application packages**: Medium buildings (crossPackageDeps 3-5)
- **Infrastructure**: Tall buildings OK (crossPackageDeps can be high)

---

### 9. Reusability vs. Coupling

**Configuration**:
```yaml
Height: fanIn (reusability)
Color: fanOut (coupling)
Area: maintenanceBurden
Filter: none
```

**Ideal Classes** (High reusability, Low coupling):
- Tall buildings (high fanIn)
- Green color (low fanOut)
- Small area (low maintenanceBurden)

**Example**: Utility classes, domain entities, interfaces

**Problematic Classes** (High coupling, Low reusability):
- Short buildings (low fanIn)
- Red color (high fanOut)
- Large area (high maintenanceBurden)

**Example**: Poorly designed orchestrators, facade classes

---

### 10. Test Impact Analysis

**Configuration**:
```yaml
Height: fanIn (how many tests break)
Color: transitiveDeps (what needs retesting)
Area: maintenanceBurden
Filter: none
Highlight: Classes changed in last commit
```

**Use Case**: Estimate test impact before making changes.

**Interpretation**:
- **Tall red buildings** = Changing this breaks many tests
- **Tall green buildings** = Changing this is isolated (good!)

---

## 📊 Comparison Configurations

### Before/After Refactoring

**Metrics to Track**:
1. **Cycle count**: Should decrease
2. **Average maintenanceBurden**: Should decrease
3. **Domain instability**: Should approach 0
4. **Classes with bidirectionalLinks**: Should decrease

**Side-by-Side View**:
```bash
# Generate before refactoring
complexity-viz run ./project --include-prefix com.example
mv dist/project dist/project-before

# Generate after refactoring
complexity-viz run ./project --include-prefix com.example
mv dist/project dist/project-after

# Compare in CodeCharta
# Load both files and use delta view
```

---

## 🚀 Quick Start Checklist

For a new project, run these configurations in order:

1. ✅ **Cycles** (cycleParticipation) - Break cycles first
2. ✅ **God Classes** (maintenanceBurden > 500) - Decompose big classes
3. ✅ **Architecture Violations** (instability by layer) - Fix dependency direction
4. ✅ **Tight Coupling** (bidirectionalLinks > 0) - Break mutual deps
5. ✅ **Breaking Change Risk** (fanIn > 20) - Protect public APIs

**Time Investment**:
- 15 minutes: Quick scan with all 5 configurations
- 2 hours: Deep dive into top 10 hotspots
- 1 week: Create refactoring plan with priorities

---

## 📈 Metrics Summary

| Metric | Good Range | Warning Range | Critical Range |
|--------|-----------|---------------|----------------|
| **cycleParticipation** | 0 | 2-4 | >5 |
| **bidirectionalLinks** | 0 | 1-2 | >3 |
| **crossPackageDeps** | 0-2 | 3-5 | >6 |
| **instability (Domain)** | 0.0-0.2 | 0.2-0.4 | >0.4 |
| **instability (Application)** | 0.3-0.5 | 0.2-0.3 or 0.5-0.7 | <0.2 or >0.7 |
| **instability (Infrastructure)** | 0.7-1.0 | 0.5-0.7 | <0.5 |
| **maintenanceBurden** | <200 | 200-500 | >500 |
| **fanIn** | <10 | 10-20 | >20 |
| **fanOut** | <5 | 5-10 | >10 |
| **transitiveDeps** | <20 | 20-50 | >50 |

---

## 🎓 Real-World Example: POSeidon V2

**Project**: 2293 classes, 8156 dependencies

### Configuration Results:

1. **Cycles**: 9 small cycles (24 classes = 1%) ✅ Excellent
2. **God Classes**: 8 classes with maintenanceBurden > 500 ⚠️ Monitor
3. **Tight Coupling**: 22 bidirectional links (0.96%) ✅ Good
4. **Architecture Violations**: Domain I=0.400 ⚠️ Investigate
5. **Breaking Change Risk**: ~50 classes with fanIn > 10 ⚠️ Document

**Overall Grade**: **A- (Well-architected with minor improvements needed)**

**Recommended Actions**:
1. Investigate why Domain instability is 0.400 (should be <0.2)
2. Monitor the 8 classes with maintenanceBurden > 500
3. Continue monitoring - architecture is healthy

---

## 💡 Pro Tips

### Tip 1: Start with the Worst
Always begin with the **Hotspots** configuration (maintenanceBurden + cycles). This gives you the "Top 10" list to focus on.

### Tip 2: Layer by Layer
Don't analyze the whole codebase at once. Use filters:
- `package contains "domain"`
- `package contains "application"`
- `package contains "infrastructure"`

### Tip 3: Compare Projects
Load 2-3 projects in CodeCharta to compare architectural quality:
- Your project
- A well-architected reference project
- A legacy monolith (as anti-pattern)

### Tip 4: Track Over Time
Run analysis every sprint/month. Track trends:
- Are cycles increasing or decreasing?
- Is average maintenanceBurden going up or down?
- Are architecture violations being fixed?

### Tip 5: Automate in CI
```bash
# .github/workflows/architecture-check.yml
- name: Analyze Architecture
  run: |
    complexity-viz run ./src --include-prefix com.company
    # Fail if cycles > 10 or average maintenanceBurden > 300
```

---

## 🔗 See Also

- [COUPLING_GUIDE.md](./COUPLING_GUIDE.md) - Detailed metric explanations
- [CodeCharta Documentation](https://maibornwolff.github.io/codecharta/) - Official docs
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) - Robert C. Martin
