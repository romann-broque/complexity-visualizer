# Quick Examples

## Basic Usage

```bash
# Analyze Java project with filtering
complexity-viz run ./my-java-project --include-prefix com.mycompany
```

**Output:** `dist/my-java-project/my-java-project.codecharta.cc.json`

---

## Real-World Examples

### Spring Boot Microservice
```bash
complexity-viz run ./user-service \
  --include-prefix com.company.userservice \
  --source ./src/main/java
```

### Multi-module Maven Project
```bash
complexity-viz run ./my-monorepo \
  --include-prefix com.company.service-a \
  --include-prefix com.company.service-b \
  --output ./architecture-analysis
```

### Clean Architecture Project (DDD)
```bash
# Focus on your domain, exclude frameworks
complexity-viz run ./ecommerce-backend \
  --include-prefix com.ecommerce \
  --no-open

# Result: Only your bounded contexts visible (no Spring/Hibernate clutter)
```

### CI/CD Integration
```bash
# Generate report without opening browser
complexity-viz run ./project \
  --include-prefix com.mycompany \
  --output ./reports/architecture \
  --no-open

# Upload ./reports/architecture/*.cc.json to artifact storage
```

---

## Recommended Workflow

1. **Compile your project first:**
   ```bash
   ./gradlew build  # or mvn compile
   ```

2. **Run analysis with filtering:**
   ```bash
   complexity-viz run . --include-prefix com.yourcompany
   ```

3. **Import to CodeCharta:**
   - Open https://maibornwolff.github.io/codecharta/visualization/app/index.html
   - Import `dist/<project-name>/<project-name>.codecharta.cc.json`

4. **Recommended visualization settings:**
   - **Height:** `fanOut` (packages with many outgoing dependencies)
   - **Color:** `complexity` (code complexity)
   - **Area:** `fanIn` (heavily used packages)
   - **Edges:** ✓ Enable (see dependency flows)

---

## Tips

### Finding your package prefix
```bash
# Look at your source structure
tree src/main/java -L 3

# Common patterns:
# com.company.*
# org.project.*
# io.github.username.*
```

### Multiple prefixes for multi-module projects
```bash
# Include multiple bounded contexts or modules
complexity-viz run . \
  --include-prefix com.company.module-a \
  --include-prefix com.company.module-b \
  --include-prefix com.company.shared
```

### Skip regeneration of .dot files
```bash
# First run generates .dot files
complexity-viz run . --include-prefix com.company

# Subsequent runs can skip this step (faster)
complexity-viz run . --include-prefix com.company --skip-dots
```
