# Complexity Visualizer

Analyze Java project dependencies and visualize architecture with CodeCharta.

## Quick Start

### Prerequisites
- Python ≥ 3.9
- Java JDK ≥ 11 (for jdeps)
- Compiled Java project

### Installation

```bash
git clone <repo>
cd complexity-visualizer
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Usage

**One command does everything:**
```bash
complexity-viz run /path/to/java-project --include-prefix com.mycompany
```

This automatically:
1. Generates dependency graphs with jdeps
2. Computes metrics (coupling, complexity, etc.)
3. Exports to CodeCharta format
4. Opens visualization in browser

**Result:** `dist/<project-name>/<project-name>.codecharta.cc.json`

**View in CodeCharta:** https://maibornwolff.github.io/codecharta/visualization/app/index.html

---

## Essential Options

| Option | Description | Example |
|--------|-------------|---------|
| `--include-prefix` | **Filter packages** (highly recommended) | `--include-prefix com.example` |
| `--source` | Java source directory (auto-detected) | `--source ./src/main/java` |
| `--output` | Custom output directory | `--output ./analysis` |
| `--skip-dots` | Use existing .dot files | `--skip-dots` |
| `--no-open` | Don't open browser | `--no-open` |

### Why use `--include-prefix`?

**Without filtering:**
```bash
complexity-viz run ./my-project
```
→ Includes ALL packages (Spring, Azure, JDK, etc.) = cluttered visualization

**With filtering:**
```bash
complexity-viz run ./my-project --include-prefix com.mycompany
```
→ Shows ONLY your project packages = clean architecture view ✅

### Multiple package prefixes
```bash
complexity-viz run ./monorepo \
  --include-prefix com.company.service-a \
  --include-prefix com.company.service-b
```

---

## Examples

### Spring Boot Microservice
```bash
complexity-viz run ./user-service \
  --include-prefix com.company.userservice
```

### Multi-module Maven Project
```bash
complexity-viz run ./my-monorepo \
  --include-prefix com.company.servicea \
  --include-prefix com.company.serviceb \
  --output ./architecture-analysis
```

### CI/CD Integration
```bash
complexity-viz run ./project \
  --include-prefix com.mycompany \
  --output ./reports/architecture \
  --no-open
```

---

## Troubleshooting

### "No compiled classes found"
**Solution:** Compile your project first:
```bash
./gradlew build    # Gradle
mvn compile        # Maven
```

### "jdeps not found"
**Solution:** Install Java JDK ≥ 11:
```bash
java -version      # Check Java version
```

### Visualization shows framework packages
**Solution:** Use `--include-prefix` to filter:
```bash
complexity-viz run ./my-project --include-prefix com.mycompany
```

### Source files not found
**Solution:** Tool auto-detects `src/main/java`. If different:
```bash
complexity-viz run ./my-project --source ./custom/src/path
```

---

## Metrics Reference

### 🟢 Structural Metrics (Always Available)

From dependency graph only - no source code required:

| Metric | Description | Problem When | Use Case |
|--------|-------------|--------------|----------|
| **fanIn** | Classes depending on this | > 50 | Breaking change risk |
| **fanOut** | Dependencies of this class | > 15 | God class detection |
| **transitiveDeps** | Total reachable deps | > 50 | Change impact radius |
| **cycleParticipation** | Cycle size (0 = no cycle) | > 0 | Circular dependencies |
| **bidirectionalLinks** | Mutual deps (A↔B) | > 0 | Tight coupling |
| **crossPackageDeps** | Package count | > 5 | Boundary violations |
| **instability** | fanOut/(fanIn+fanOut) | Domain: >0.2<br>Infra: <0.8 | Architecture audit |

### 🟡 Code Analysis Metrics (Requires `--source`)

From Java source files:

| Metric | Description | Problem When |
|--------|-------------|--------------|
| **complexity** | Cyclomatic complexity | > 20 |
| **loc** | Lines of code | > 500 |
| **methods** | Method count | > 30 |
| **maintenanceBurden** | (transitiveDeps × fanIn) + complexity² | > 500 |

**Note:** `maintenanceBurden` uses only `(transitiveDeps × fanIn)` without `--source`, but adds `complexity²` when source is available for full score.

### Metric Thresholds

| Metric | Good ✅ | Warning ⚠️ | Critical ❌ |
|--------|---------|-----------|-------------|
| cycleParticipation | 0 | 2-4 | >5 |
| bidirectionalLinks | 0 | 1-2 | >3 |
| crossPackageDeps | 0-2 | 3-5 | >6 |
| instability (Domain) | 0.0-0.2 | 0.2-0.4 | >0.4 |
| maintenanceBurden | <200 | 200-500 | >500 |
| fanIn | <10 | 10-20 | >20 |
| fanOut | <5 | 5-10 | >10 |
| transitiveDeps | <20 | 20-50 | >50 |

---

## CodeCharta Configurations

Ready-to-use configurations for common analysis tasks:

### 1. 🔴 Find Dependency Cycles (Highest Priority)
```
Height: cycleParticipation
Color:  maintenanceBurden
Area:   fanIn
Filter: cycleParticipation > 0
```
**Interpretation:**
- Tall buildings = Large cycles (hard to break)
- Red color = High maintenance burden
- No buildings = No cycles ✅

### 2. 👹 Detect God Classes
```
Height: maintenanceBurden
Color:  fanIn
Area:   transitiveDeps
Filter: maintenanceBurden > 500
```
**Interpretation:**
- Tallest buildings = Hardest to maintain
- Red color = Many dependents (breaking change risk)
- Large area = Wide blast radius

### 3. 🏗️ Validate Clean Architecture
```
Height: instability
Color:  crossPackageDeps
Area:   fanIn
Filter: package contains "domain"
```
**Expected:**
- Domain: Short buildings (I < 0.2), green color
- Application: Medium buildings (I ≈ 0.3-0.5)
- Infrastructure: Tall buildings (I ≈ 0.7-1.0)

**Violations:**
- ❌ Tall buildings in domain = Domain depends on infrastructure
- ❌ Red domain classes = Too many package dependencies

### 4. 🔗 Identify Tight Coupling
```
Height: bidirectionalLinks
Color:  crossPackageDeps
Area:   fanIn
Filter: bidirectionalLinks > 0
```
**Interpretation:**
- Tall buildings = Many mutual dependencies (A↔B)
- Red color = Crosses package boundaries
- Action: Introduce interfaces (Dependency Inversion)

### 5. 💥 Breaking Change Risk
```
Height: fanIn
Color:  maintenanceBurden
Area:   transitiveDeps
Filter: fanIn > 10
```
**Interpretation:**
- Tallest buildings = Most depended-upon classes
- Red color = High change impact
- Action: Version API carefully or decompose

### 6. 🕸️ Dependency Hell
```
Height: transitiveDeps
Color:  fanOut
Area:   fanIn
Filter: transitiveDeps > 50
```
**Interpretation:**
- Tallest buildings = Longest dependency chains
- Red color = Many direct dependencies
- Action: Introduce layers, break chains

### 7. 🔥 Overall Hotspots (Refactoring Priorities)
```
Height: maintenanceBurden
Color:  cycleParticipation
Area:   fanIn
Filter: maintenanceBurden > 200
Sort:   Height descending
```
**Risk Matrix:**
- maintenanceBurden >1000 + cycle >0 = 🔥 URGENT
- maintenanceBurden >1000 + no cycle = ❌ HIGH
- maintenanceBurden 500-1000 + cycle = ⚠️ MEDIUM

---

## Understanding Instability (Robert C. Martin)

**Formula:** `I = fanOut / (fanIn + fanOut)`

**Range:** 0.0 (stable) → 1.0 (unstable)

**Clean Architecture expectations:**
- **Domain (0.0-0.2):** Stable core, no outgoing dependencies
- **Application (0.3-0.5):** Moderate, orchestrates domain
- **Infrastructure (0.7-1.0):** Unstable, depends on everything

**Problem indicators:**
- Domain I > 0.3 = Domain depends on infrastructure ❌
- Infrastructure I < 0.5 = Infrastructure is too stable (leaky abstraction) ❌

---

## Advanced: Step-by-Step Pipeline

If you need more control, run each step individually:

```bash
# 1. Generate .dot files
complexity-viz generate-dots ./my-project --include-prefix com.example

# 2. Build graph and compute metrics
complexity-viz build-graph ./dist/my-project \
  --include-prefix com.example \
  --source ./src/main/java

# 3. Convert to CodeCharta format
complexity-viz convert ./dist/my-project/my-project.metrics.json

# 4. Open visualization
complexity-viz visualize ./dist/my-project/my-project.codecharta.cc.json
```

---

## Output Structure

```
dist/
└── my-project/
    ├── dots/                           # jdeps .dot files
    ├── my-project.metrics.json         # Intermediate metrics
    └── my-project.codecharta.cc.json   # ← Import this in CodeCharta
```

---

## Architecture

```
complexity-visualizer/
├── commands/          # CLI commands (run, generate-dots, build-graph, convert, visualize)
├── core/              # Graph parsing, metrics computation, algorithms
├── exporters/         # CodeCharta & intermediate JSON export
├── analyzers/         # Java source code analysis
└── utils/             # jdeps runner, auto-detection, browser opener
```

---

## Pro Tips

### Tip 1: Start with Hotspots
Begin with the **Hotspots** configuration (maintenanceBurden + cycles) to get your "Top 10" list.

### Tip 2: Layer by Layer
Use filters to analyze specific layers:
- `package contains "domain"`
- `package contains "application"`
- `package contains "infrastructure"`

### Tip 3: Track Over Time
Run analysis every sprint/month. Track trends:
- Are cycles increasing or decreasing?
- Is average maintenanceBurden going up or down?

### Tip 4: Before/After Comparison
```bash
# Before refactoring
complexity-viz run ./project --include-prefix com.example
mv dist/project dist/project-before

# After refactoring
complexity-viz run ./project --include-prefix com.example
mv dist/project dist/project-after

# Compare in CodeCharta using delta view
```

### Tip 5: Skip .dot Regeneration
```bash
# First run generates .dot files
complexity-viz run . --include-prefix com.company

# Subsequent runs can skip this step (faster)
complexity-viz run . --include-prefix com.company --skip-dots
```

---

## References

- **Cyclomatic Complexity:** McCabe (1976)
- **Instability Metric:** Robert C. Martin, "Clean Architecture"
- **CodeCharta:** https://maibornwolff.github.io/codecharta/
- **Acyclic Dependencies Principle:** https://en.wikipedia.org/wiki/Acyclic_dependencies_principle
