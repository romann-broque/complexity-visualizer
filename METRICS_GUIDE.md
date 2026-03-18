# Metrics Reference Guide

Quick reference for all computed metrics with focus on **coupling analysis**.

---

## Metric Categories

**🟢 Structural (always available)** - From `.dot` files only  
**🟡 Code Analysis (requires `--source`)** - From Java source files

---

## Structural Metrics (🟢 Always Available)

### fanIn
**What:** Classes that depend on this class (incoming edges)  
**Problem:** > 50 = Critical hub, high blast radius  
**Use:** Measure change impact, find central abstractions  
**CodeCharta:** Area or Height to emphasize importance

### fanOut
**What:** Classes this class depends on (outgoing edges)  
**Problem:** > 15 = God class, SRP violation  
**Use:** Find God classes, measure coupling  
**CodeCharta:** Area or Height to spot violations

### transitiveDeps
**What:** Total reachable dependencies (recursive)  
**Problem:** > 50 = High change propagation risk  
**Use:** Blast radius, refactoring risk assessment  
**CodeCharta:** Height to emphasize impact

### cycleParticipation
**What:** Size of dependency cycle (0 = no cycle)  
**Problem:** > 0 = Circular dependencies  
**Solution:** Dependency Inversion Principle  
**CodeCharta:** Color (red) or Height

### bidirectionalLinks
**What:** Mutual dependencies (A→B AND B→A)  
**Problem:** > 0 = Tight coupling  
**Solution:** Extract interface, add mediator  
**CodeCharta:** Color to highlight tight coupling

### crossPackageDeps
**What:** Number of different packages used  
**Problem:** > 5 = Bounded context violations  
**Use:** Clean Architecture audits  
**CodeCharta:** Area or Color for architecture review

### instability
**What:** `fanOut / (fanIn + fanOut)` - Martin's metric  
**Range:** 0.0 (stable) → 1.0 (unstable)  
**Expected:**
- Domain: 0.0-0.2 (stable core)
- Application: 0.3-0.5 (moderate)
- Infrastructure: 0.8-1.0 (unstable, depends on all)

**Problem:** Domain > 0.3 = architecture violation  
**CodeCharta:** Color to audit Clean Architecture

---

## Code Analysis Metrics (🟡 Requires `--source`)

### complexity
**What:** Cyclomatic complexity (decision points + 1)  
**Problem:** > 20 = Very complex, high bug risk  
**CodeCharta:** Height or Color for hotspots

### loc
**What:** Lines of code (non-empty, non-comment)  
**Problem:** > 500 = SRP violation  
**CodeCharta:** Area to show size

### methods
**What:** Method count  
**Problem:** > 30 = God class  
**CodeCharta:** Combine with loc for density

### maintenanceBurden
**What:** `(transitiveDeps × fanIn) + complexity²`  
**Without --source:** Only `(transitiveDeps × fanIn)`  
**Problem:** > 2000 = Critical refactoring priority  
**Why:** Combines impact + difficulty  
**CodeCharta:** Color for refactoring priorities

---

## CodeCharta Configurations

### Config 1: God Class Detection
```
Area:   fanOut
Height: transitiveDeps
Color:  bidirectionalLinks (or complexity with --source)
```

### Config 2: Clean Architecture Audit
```
Area:   crossPackageDeps
Height: fanOut
Color:  instability
```

### Config 3: Refactoring Priorities
```
Area:   fanIn
Height: maintenanceBurden
Color:  cycleParticipation
```

### Config 4: Coupling Hotspots
```
Area:   transitiveDeps
Height: fanOut
Color:  bidirectionalLinks
```

---

## Quick Decision Guide

| Symptom | Metric | Threshold | Action |
|---------|--------|-----------|--------|
| God class | fanOut | > 15 | Split into smaller classes |
| Central hub | fanIn | > 50 | Extract interface, reduce coupling |
| Circular deps | cycleParticipation | > 0 | Dependency Inversion |
| Tight coupling | bidirectionalLinks | > 0 | Mediator or event bus |
| Boundary violation | crossPackageDeps | > 5 | Respect bounded contexts |
| Unstable domain | instability | > 0.2 | Remove infra dependencies |
| High change risk | transitiveDeps | > 50 | Isolate, add tests |
| Complex code | complexity | > 20 | Simplify, extract methods |

---

## Best Practices

✅ **Always use `--source`** for complete analysis  
✅ **Filter with `--include-prefix`** to exclude libraries  
✅ **Try multiple configurations** to spot different problems  
✅ **Focus on actionable hotspots** (top 5-10 classes)

---

## Troubleshooting

**Q: loc/methods are 0**  
A: Add `--source ./src/main/java`

**Q: maintenanceBurden seems low**  
A: Need `--source` for complexity component

**Q: Too many nodes**  
A: Use `--include-prefix com.yourcompany`

---

## References

- Cyclomatic Complexity: McCabe (1976)
- Instability: Martin, "Clean Architecture"
- Maintenance Burden: Custom composite metric
