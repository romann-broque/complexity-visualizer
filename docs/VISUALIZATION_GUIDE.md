# CodeCharta Visualization Guide

## Available Metrics for Visualization

All metrics are exported as node attributes in the CodeCharta JSON and can be mapped to Area, Height, or Color.

---

## Metrics Reference

### Basic Coupling Metrics

| Metric | Type | Range | Description |
|--------|------|-------|-------------|
| `fanIn` | absolute | 0+ | Number of classes that depend on this class |
| `fanOut` | absolute | 0+ | Number of classes this class depends on |
| `totalCoupling` | absolute | 0+ | fanIn + fanOut (total connectivity) |
| `stability` | relative | 0.0-1.0 | Resistance to change (high = stable) |
| `instability` | relative | 0.0-1.0 | Likelihood of change (high = unstable) |

### Enhanced Dependency Metrics

| Metric | Type | Range | Description |
|--------|------|-------|-------------|
| `transitiveDeps` | absolute | 0+ | Total number of classes transitively reachable |
| `isInCycle` | absolute | 0/1 | 1 if class is in a circular dependency |
| `cycleSize` | absolute | 0+ | Size of the cycle this class belongs to |

### Strategic Refactoring Indicators

| Metric | Type | Range | Description |
|--------|------|-------|-------------|
| `isBreakingPoint` | absolute | 0/1 | 1 if removing this class breaks cycles |
| `isHighImpact` | absolute | 0/1 | 1 if changes to this class affect many others |
| `isHubNode` | absolute | 0/1 | 1 if totalCoupling ≥ 10 |

### Architectural Classification

| Metric | Type | Range | Description |
|--------|------|-------|-------------|
| `isLeafNode` | absolute | 0/1 | 1 if class has no dependencies (fanOut = 0) |
| `isRootNode` | absolute | 0/1 | 1 if nothing depends on this class (fanIn = 0) |
| `unresolved` | absolute | 0/1 | 1 if class has unresolved dependencies |

---

## Recommended Visualization Configurations

### 1. Problem Detection (Default) 🔴

**Goal**: Identify unstable, highly coupled classes

```json
{
  "area": "fanIn",
  "height": "fanOut",
  "color": "instability"
}
```

**Interpretation**:
- **Large buildings** = Many classes depend on this (high fanIn) → Stability concern
- **Tall buildings** = Depends on many classes (high fanOut) → Change risk
- **Red color** = High instability → Needs attention
- **Red + Large + Tall** = Critical problem class

**What to look for**:
- Red skyscrapers = Unstable hub classes (refactor priority)
- Large red areas = Stable but highly depended upon (add tests before touching)

---

### 2. Circular Dependency Detection 🔵

**Goal**: Find and visualize circular dependencies

```json
{
  "area": "totalCoupling",
  "height": "cycleSize",
  "color": "isInCycle"
}
```

**Interpretation**:
- **Tall buildings** = Part of large circular dependency
- **Red/colored** = In a cycle (1 = yes)
- **Large area** = Highly coupled class
- **Tall + Colored + Large** = Core of tangled architecture

**What to look for**:
- Clusters of colored buildings = Circular dependency zones
- Tallest colored buildings = Largest cycles (hardest to break)

---

### 3. Refactoring Impact Analysis 🟡

**Goal**: Identify high-impact changes and refactoring targets

```json
{
  "area": "transitiveDeps",
  "height": "totalCoupling",
  "color": "isHighImpact"
}
```

**Interpretation**:
- **Large footprint** = Changes propagate widely (high transitive deps)
- **Tall** = Highly connected class
- **Colored** = High-impact class (needs extensive testing)

**What to look for**:
- Colored skyscrapers = Test these thoroughly before refactoring
- Large colored areas = Changes here affect the whole system

---

### 4. Strategic Refactoring Targets 🟢

**Goal**: Find the best classes to refactor first

```json
{
  "area": "fanOut",
  "height": "cycleSize",
  "color": "isBreakingPoint"
}
```

**Interpretation**:
- **Tall buildings** = In large cycles
- **Colored (green)** = Breaking point node (strategic target)
- **Large + Tall + Colored** = Refactor this to break multiple cycles

**What to look for**:
- Green tall buildings = Refactor these first for maximum cycle reduction
- Isolated green = Easy breaking points

---

### 5. Architectural Health Overview 🟣

**Goal**: Understand overall system structure

```json
{
  "area": "totalCoupling",
  "height": "transitiveDeps",
  "color": "isHubNode"
}
```

**Interpretation**:
- **Large + Tall** = Central architectural component
- **Colored** = Hub node (high coupling)
- **Many colored buildings** = Over-centralized architecture

**What to look for**:
- Colored skyscrapers = System bottlenecks
- Flat, small, uncolored = Well-isolated components (good)

---

### 6. Dead Code Detection 💀

**Goal**: Find unused or isolated code

```json
{
  "area": "fanIn",
  "height": "fanOut",
  "color": "isRootNode"
}
```

**Interpretation**:
- **Small + Flat + Colored** = Nothing depends on it, it depends on nothing → Dead code?
- **Large + Flat + Colored** = API entry points or public interfaces

**What to look for**:
- Small colored flat buildings = Candidates for deletion
- Large colored buildings = Entry points (keep)

---

### 7. Stability Analysis 📊

**Goal**: Identify stable vs volatile areas

```json
{
  "area": "fanIn",
  "height": "fanOut",
  "color": "stability"
}
```

**Interpretation**:
- **Green/high stability** = Stable, depended upon (good for core libraries)
- **Red/low stability** = Volatile, many dependencies (good for app layer)
- **Large green buildings** = Stable core components (don't change)
- **Large red buildings** = Unstable hubs (problem)

**What to look for**:
- Inversion = Red buildings at bottom (stable layer), green at top (app layer) → Architecture issue

---

## Usage Workflow

### 1. Initial Health Check
Start with **Problem Detection** configuration:
```
Area: fanIn
Height: fanOut  
Color: instability
```

Look for:
- Red skyscrapers → Priority refactoring targets
- Clusters of red → Problematic modules

### 2. Identify Cycles
Switch to **Circular Dependency Detection**:
```
Area: totalCoupling
Height: cycleSize
Color: isInCycle
```

Count colored buildings → Number of classes in cycles

### 3. Plan Refactoring
Use **Strategic Refactoring Targets**:
```
Area: fanOut
Height: cycleSize
Color: isBreakingPoint
```

Green buildings are your refactoring priorities

### 4. Assess Impact
Before refactoring, check **Refactoring Impact**:
```
Area: transitiveDeps
Height: totalCoupling
Color: isHighImpact
```

Colored buildings need comprehensive tests first

### 5. Monitor Progress
After refactoring, revisit **Problem Detection** and **Circular Dependency Detection** to verify improvements

---

## Color Schemes Recommendations

For binary metrics (`isInCycle`, `isBreakingPoint`, `isHubNode`, etc.):
- Use **categorical colors**: Red (1) / Green (0) or Blue (1) / Gray (0)

For continuous metrics (`instability`, `stability`, `fanIn`, `fanOut`):
- Use **gradient**: Green (low) → Yellow (medium) → Red (high)

For CodeCharta configuration:
- Set color ranges appropriately for each metric type
- Use logarithmic scale for metrics with wide ranges

---

## Package-Level Aggregation

CodeCharta automatically aggregates metrics for packages (folders):
- **Sum**: fanIn, fanOut, totalCoupling, transitiveDeps, cycleSize
- **Average**: stability, instability
- **Max**: isInCycle, isBreakingPoint, isHighImpact (1 if any child is 1)

**Interpretation at package level**:
- Large package buildings = High total coupling → Monolithic module
- Tall colored packages = Contains many classes in cycles
- Small flat packages = Well-isolated, independent modules (good)

---

## Example Analysis Session

**Scenario**: You load your project in CodeCharta

**Step 1**: Configure Problem Detection
```
Area: fanIn | Height: fanOut | Color: instability
```
**Observation**: 3 large red skyscrapers in `com.myapp.core` package

**Step 2**: Switch to Cycle Detection
```
Area: totalCoupling | Height: cycleSize | Color: isInCycle
```
**Observation**: All 3 buildings are colored and tall (cycle size 15)

**Step 3**: Find Breaking Points
```
Area: fanOut | Height: cycleSize | Color: isBreakingPoint
```
**Observation**: 1 of the 3 is green (breaking point)

**Step 4**: Check Impact
```
Area: transitiveDeps | Height: totalCoupling | Color: isHighImpact
```
**Observation**: The breaking point class is colored (high impact)

**Action Plan**:
1. Write comprehensive tests for the high-impact breaking point class
2. Refactor it to break the cycle of 15 classes
3. Re-run visualization to verify cycle elimination

---

## Tips and Tricks

1. **Start with packages collapsed**: Get high-level view first, then drill down
2. **Compare before/after**: Export visualizations before and after refactoring
3. **Use filters**: CodeCharta allows filtering by metric values (e.g., show only `isInCycle = 1`)
4. **Combine metrics**: Look for intersections (e.g., high instability AND in cycle)
5. **Watch for patterns**: Scattered problems vs. concentrated problems indicate different issues
6. **Package boundaries**: If cycles cross package boundaries, you have architectural issues
7. **Temporal analysis**: If CodeCharta supports it, track metrics over time

---

## Metric Combinations for Specific Questions

| Question | Area | Height | Color |
|----------|------|--------|-------|
| Which classes are architectural bottlenecks? | `fanIn` | `fanOut` | `isHubNode` |
| Where are the circular dependencies? | `totalCoupling` | `cycleSize` | `isInCycle` |
| Which classes should I test before refactoring? | `transitiveDeps` | `totalCoupling` | `isHighImpact` |
| What's the fastest way to reduce cycles? | `fanOut` | `cycleSize` | `isBreakingPoint` |
| Is my architecture stable? | `fanIn` | `fanOut` | `stability` |
| Do I have dead code? | `fanIn` | `fanOut` | `isRootNode` |
| Which packages are most complex? | `totalCoupling` | `transitiveDeps` | `cycleSize` |