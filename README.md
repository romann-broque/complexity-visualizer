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

## Metrics Computed

The tool computes several coupling and complexity metrics:

### Basic Metrics
- **fanIn**: Number of classes depending on this class
- **fanOut**: Number of direct dependencies
- **transitiveDeps**: Total reachable classes (blast radius)
- **complexity**: Cyclomatic complexity (from source)
- **loc**: Lines of code (from source)
- **methods**: Number of methods (from source)

### Coupling Metrics (New!)
- **cycleParticipation**: Size of dependency cycle (0 = no cycle)
- **bidirectionalLinks**: Mutual dependencies count (A→B AND B→A)
- **crossPackageDeps**: Number of different packages depended upon
- **instability**: Robert C. Martin's stability metric (0 = stable, 1 = unstable)
- **maintenanceBurden**: Composite change impact score

**See [COUPLING_GUIDE.md](./COUPLING_GUIDE.md) for detailed usage and visualization strategies.**

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