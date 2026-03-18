# Complexity Visualizer

Analyze Java project dependencies and visualize architecture with CodeCharta.

## Quick Start

### Prerequisites
- Python ≥ 3.9
- Java JDK ≥ 11 (for jdeps)
- Compiled Java project

### Installation

```bash
# Clone and install
git clone <repo>
cd complexity-visualizer
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Usage

**Simple - One command:**
```bash
complexity-viz run /path/to/java-project --include-prefix com.mycompany
```

This automatically:
1. Generates dependency graphs with jdeps
2. Computes metrics
3. Exports to CodeCharta format
4. Opens visualization in browser

**Result:** `dist/<project-name>/<project-name>.codecharta.cc.json`

---

## Options

### Essential Options

| Option | Description | Example |
|--------|-------------|---------|
| `--include-prefix` | **Filter packages** (highly recommended) | `--include-prefix com.example` |
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

---

## Examples

### Basic usage (with filtering)
```bash
complexity-viz run ./poseidon-backend \
  --include-prefix com.totalenergies.poseidon2
```

### Advanced usage
```bash
complexity-viz run ./my-microservice \
  --include-prefix com.example \
  --output ./reports/architecture \
  --source ./src/main/java \
  --no-open
```

### Multiple package prefixes
```bash
complexity-viz run ./monorepo \
  --include-prefix com.company.service-a \
  --include-prefix com.company.service-b
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

**View in CodeCharta:** https://maibornwolff.github.io/codecharta/visualization/app/index.html

---

## Advanced: Step-by-Step Pipeline

If you need more control, run each step individually:

```bash
# 1. Generate .dot files
complexity-viz generate-dots ./my-project --include-prefix com.example

# 2. Build graph and compute metrics
complexity-viz build-graph ./from/my-project \
  --include-prefix com.example \
  --output ./dist

# 3. Convert to CodeCharta format
complexity-viz convert ./dist/metrics.json

# 4. Open visualization
complexity-viz visualize ./dist/codecharta.cc.json
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

---

## Metrics Overview

### Available Metrics

**🟢 Structural (always available)** - From `.dot` files:

| Metric | Description | Problem When |
|--------|-------------|--------------|
| **fanIn** | Classes depending on this | > 50 (hub) |
| **fanOut** | Dependencies of this class | > 15 (God class) |
| **transitiveDeps** | Total reachable deps | > 50 (high impact) |
| **cycleParticipation** | Cycle size | > 0 (circular deps) |
| **bidirectionalLinks** | Mutual deps (A↔B) | > 0 (tight coupling) |
| **crossPackageDeps** | Package count | > 5 (boundary violation) |
| **instability** | fanOut/(fanIn+fanOut) | Domain: >0.2, Infra: <0.8 |

**🟡 Code Analysis (requires `--source`)** - From source files:

| Metric | Description | Requires |
|--------|-------------|----------|
| **complexity** | Cyclomatic complexity | `--source` |
| **loc** | Lines of code | `--source` |
| **methods** | Method count | `--source` |
| **maintenanceBurden** | (transitiveDeps × fanIn) + complexity² | `--source` for full score |

### Quick CodeCharta Configs

| Goal | Area | Height | Color |
|------|------|--------|-------|
| Find God classes | fanOut | transitiveDeps | instability |
| Detect tight coupling | transitiveDeps | fanOut | bidirectionalLinks |
| Audit architecture | crossPackageDeps | fanOut | cycleParticipation |
| Refactoring priorities | fanIn | maintenanceBurden | cycleParticipation |

**📚 For details, thresholds, and examples:** [METRICS_GUIDE.md](./METRICS_GUIDE.md)

---

## Architecture

```
complexity-visualizer/
├── commands/          # CLI commands (run, generate-dots, build-graph, convert, visualize)
├── core/              # Graph parsing, metrics computation
├── exporters/         # CodeCharta export
├── analyzers/         # Java source code analysis
└── utils/             # jdeps runner, auto-detection
```