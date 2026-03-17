# Complexity Visualizer v2.0

Analyze software complexity and visualize with CodeCharta.

**Major improvements in v2:**
- 🎯 Clear pipeline commands: `generate-dots`, `build-graph`, `convert`, `visualize`, `run`
- 🚀 All-in-one `run` command for simplicity
- 🔄 Simplified architecture with modular commands
- 📊 Flexible intermediate JSON format
- 🔍 Auto-detection of Maven/Gradle projects
- 🐛 Critical bugs fixed
- 📦 No external dependencies (pure Python stdlib)

## Quick Start

### Prerequisites
- Python ≥ 3.9
- Java JDK ≥ 11 (for jdeps)
- Your project must be compiled first

### Installation

```bash
# 1. Clone and navigate
git clone <repo>
cd complexity-visualizer

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install
pip install -e .
```

**Note:** Always activate the virtual environment before using the tool:
```bash
source .venv/bin/activate
complexity-viz --help
```

### Usage

#### Option 1: All-in-One Command (Simplest)

```bash
# One command does everything
complexity-viz run ./my-project
```

This automatically:
1. ✅ Generates .dot files with jdeps
2. ✅ Builds dependency graph and computes metrics
3. ✅ Converts to CodeCharta format
4. ✅ Opens visualization in your browser

**Common options:**
```bash
# Specify custom output directory (default: ./dist/<project-name>)
complexity-viz run ./my-project --output ./analysis-results

# Filter specific packages
complexity-viz run ./my-project --include-prefix com.example

# Specify source directory
complexity-viz run ./my-project --source ./src/main/java

# Skip .dot generation (use existing)
complexity-viz run ./my-project --skip-dots

# Don't open browser
complexity-viz run ./my-project --no-open
```

**Output Structure:**

By default, files are organized in `./dist/<project-name>/`:

```
dist/
└── my-project/                      # Project-specific subdirectory
    ├── dots/                        # .dot dependency files
    ├── my-project.metrics.json      # Intermediate metrics
    └── my-project.codecharta.cc.json # Final visualization file
```

This allows analyzing multiple projects without conflicts:
```
dist/
├── project-a/
│   ├── dots/
│   ├── project-a.metrics.json
│   └── project-a.codecharta.cc.json
└── project-b/
    ├── dots/
    ├── project-b.metrics.json
    └── project-b.codecharta.cc.json
```

You can specify a custom output directory with `--output` (no subdirectory added):
```bash
complexity-viz run ./my-project --output ./my-analysis
# Output: ./my-analysis/dots/, ./my-analysis/my-project.metrics.json, etc.
```

#### Option 2: Step-by-Step Pipeline (Advanced)

For more control, use individual commands:

```bash
# Step 1: Generate .dot files using jdeps
complexity-viz generate-dots ./my-project --output ./analysis/dots

# Step 2: Build graph and compute metrics
complexity-viz build-graph ./analysis/dots \
  --source ./my-project/src/main/java \
  --output ./analysis

# Step 3: Convert to CodeCharta format
complexity-viz convert ./analysis/metrics.json

# Step 4: Open visualization
complexity-viz visualize ./analysis/codecharta.cc.json
```

**Why use step-by-step?**
- Full control over each output directory
- Debug specific steps independently
- Regenerate only what changed
- CI/CD integration with custom paths

#### Command Reference

| Command | Purpose | Input | Output |
|---------|---------|-------|--------|
| `generate-dots` | Run jdeps to generate .dot files | Compiled classes | .dot files |
| `build-graph` | Parse .dot and compute metrics | .dot files | metrics.json |
| `convert` | Convert to CodeCharta format | metrics.json | codecharta.cc.json |
| `visualize` | Open in CodeCharta | codecharta.cc.json | Browser |
| `run` | Execute all steps | Project path | Everything |

**Get help for any command:**
```bash
complexity-viz <command> --help
```

### Viewing Results

The generated `.cc.json` file can be visualized in **CodeCharta**, an interactive 3D code visualization tool.

#### Option 1: Online CodeCharta (Recommended - No Installation)

**Quickest way to get started:**

1. **Open CodeCharta Web Studio** in your browser:
   ```
   https://codecharta.com/visualization/app/index.html
   ```

2. **Load your file:**
   - Click the **"Load File"** button in the interface, OR
   - Drag and drop your `dist/codecharta.cc.json` file

3. **Explore!** Your codebase is now visualized in 3D!

**What you'll see:**
- **Buildings** = Classes/Files
  - **Height** = Complexity (cyclomatic complexity)
  - **Color** = Maintenance Burden (red/orange = hotspots)
  - **Area** = Lines of Code
- **Districts** = Packages/Folders
- **Red/Orange areas** = Hotspots requiring attention

**Navigation:**
- **Left click + drag** = Rotate view
- **Right click + drag** = Pan
- **Scroll wheel** = Zoom in/out
- **Click on building** = View detailed metrics

**Privacy:** All processing happens in your browser. Your code never leaves your machine.

#### Option 2: Quick Open with CLI

The `visualize` command automatically opens CodeCharta:

```bash
complexity-viz visualize ./dist/codecharta.cc.json
```

This will:
- Display instructions
- Automatically open your browser (macOS/Linux/Windows)
- Show you where to drag & drop the file

#### Option 3: Local CodeCharta (Advanced Users)

If you prefer running CodeCharta locally:

```bash
# One-time setup
git clone https://github.com/MaibornWolff/codecharta.git
cd codecharta/visualization
npm install

# Start the local server
npm run dev
# Opens at http://localhost:9000
```

Then load your `dist/codecharta.cc.json` file in the interface.

**When to use local:**
- Corporate networks with restricted internet access
- Very large codebases (100+ MB files)
- Custom CodeCharta modifications
- Offline development

### Understanding the Visualization

CodeCharta uses a **city metaphor** to represent your codebase:

#### Visual Elements

**🏢 Buildings = Classes/Files**
- Each building represents a class or file in your codebase
- Taller buildings = Higher complexity
- Larger footprint = More lines of code
- Color coding = Different metrics (customizable)

**🏘️ Districts = Packages/Folders**
- Groups of buildings represent packages or directories
- District boundaries help you understand architecture
- Navigate by clicking to zoom into packages

**🎨 Color Coding (Default)**
- **Green** = Low maintenance burden, healthy code
- **Yellow** = Moderate burden, worth monitoring
- **Orange** = High burden, consider refactoring
- **Red** = Critical hotspot, technical debt

#### What to Look For

**🔥 Hotspots (Red/Orange Buildings)**
- Classes with high maintenance burden
- Complex code with many dependencies
- High risk when making changes
- **Action:** Prioritize for refactoring or testing

**🏗️ Tall, Wide Buildings**
- Large, complex classes (God classes)
- Violate Single Responsibility Principle
- Difficult to understand and maintain
- **Action:** Consider breaking into smaller classes

**🕸️ Dense Districts**
- Tightly coupled packages
- Many internal dependencies
- Changes cascade through the system
- **Action:** Review architecture, reduce coupling

**🏚️ Isolated Buildings**
- Low fan-in (few dependencies on them)
- Could indicate dead code or utilities
- **Action:** Verify if still needed

#### Tips for Effective Analysis

1. **Start with the bird's-eye view**: Get overall architecture sense
2. **Filter by package**: Focus on specific areas of concern
3. **Compare metrics**: Switch between complexity, LOC, and maintenance burden
4. **Use edges**: Enable dependency edges to see coupling
5. **Track over time**: Compare multiple snapshots to see trends

## Architecture

### New Structure (v2)

```
complexity_visualizer/
├── commands/          # CLI commands (one per file)
│   ├── generate_dots.py  # Step 1: Generate .dot files
│   ├── build_graph.py    # Step 2: Build graph & metrics
│   ├── convert.py        # Step 3: Convert to CodeCharta
│   ├── visualize.py      # Step 4: Open visualization
│   └── run.py            # All-in-one pipeline
├── analyzers/         # Language-specific analyzers
│   ├── base.py        # Abstract interface
│   └── java.py        # Java analyzer
├── core/              # Core logic
│   ├── graph_builder.py
│   ├── metrics.py
│   ├── models.py
│   └── parsers.py
├── exporters/         # Output formats
│   ├── intermediate.py  # Flexible JSON format
│   └── codecharta.py    # CodeCharta converter
├── utils/             # Utilities
│   ├── auto_detect.py   # Project detection
│   ├── jdeps_runner.py  # jdeps execution
│   └── browser_opener.py
└── cli.py             # CLI entry point
```

### Formats

**1. Intermediate Format (metrics.json)**
- Flexible pivot format
- Rich metadata (aggregates, hotspots, packages)
- Easy to extend with custom metrics

**2. CodeCharta Format (.cc.json)**
- 3D visualization
- Interactive exploration
- Industry standard

**3. Legacy Format (graph.json)**
- Backward compatibility
- Used by existing scripts

## Metrics Explained

- **Fan-In:** Number of classes depending on this class (incoming dependencies)
- **Fan-Out:** Number of classes this class depends on (outgoing dependencies)
- **Transitive Deps:** Total number of reachable classes through dependencies
- **Complexity:** Cyclomatic complexity (number of decision points in code)
- **LOC:** Lines of code (non-empty, non-comment)
- **Methods:** Number of methods in the class
- **Maintenance Burden:** Composite score = `(transitiveDeps × fanIn) + cyclePenalty²`
  - High burden = difficult to modify safely
  - Identifies technical debt hotspots

## Workflow Example

### Complete Example: Analyzing a Maven Project

```bash
# 1. Compile your project
cd /path/to/my-java-project
mvn compile

# 2. Run full analysis (one command)
cd /path/to/complexity-visualizer
source .venv/bin/activate
complexity-viz run ../my-java-project \
  --source ../my-java-project/src/main/java \
  --include-prefix com.mycompany

# Done! Browser opens with 3D visualization
# Default output: ./dist/my-java-project/
# Done! Browser opens with 3D visualization
# Default output: ./dist/my-java-project/
#   ├── dots/
#   ├── my-java-project.metrics.json
#   └── my-java-project.codecharta.cc.json

# Or specify custom output:
complexity-viz run ../my-java-project --output ./custom-results
```

### Step-by-Step Example

```bash
# 1. Compile project
cd /path/to/my-java-project
mvn compile

# 2. Generate .dot files
cd /path/to/complexity-visualizer
source .venv/bin/activate
complexity-viz generate-dots ../my-java-project --output ./analysis/dots

# 3. Build graph and compute metrics
complexity-viz build-graph ./analysis/dots \
  --source ../my-java-project/src/main/java \
  --include-prefix com.mycompany \
  --output ./analysis \
  --project "My Project"

# 4. Convert to CodeCharta
complexity-viz convert ./analysis/My\ Project.metrics.json --project "My Project"

# 5. Visualize
complexity-viz visualize ./analysis/My\ Project.codecharta.cc.json
```

### Working with Existing .dot Files

If you already have .dot files:

```bash
# Skip .dot generation and use existing files
complexity-viz run ./path/to/dot-files --skip-dots --output ./results

# Or use step-by-step starting from step 2
complexity-viz build-graph ./path/to/dots --source ./src --output ./analysis
```

## Troubleshooting

### `error: externally-managed-environment`

**Problem:** Can't install with `pip install -e .`

**Solution:** Use a virtual environment (required on macOS/Linux):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### `command not found: complexity-viz`

**Problem:** Command not available after installation

**Solution:** Activate the virtual environment:
```bash
source .venv/bin/activate
```

### `.dot files not found`

**Problem:** No .dot files detected during analysis

**Solution:** 
1. Ensure your project is compiled
2. Run jdeps to generate .dot files:
```bash
# For Maven projects
jdeps -dotoutput ./from/myproject target/classes/**/*.class

# For Gradle projects  
jdeps -dotoutput ./from/myproject build/classes/**/*.class
```
3. Specify manually: `--dot ./from/myproject`

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest tests/
```
