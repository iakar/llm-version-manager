# 🏗️ Architecture Guide

## System Overview

LLM Version Manager is designed as a modular system with four main components:

```
┌─────────────┐
│   CLI Tool  │ ← User interface
└──────┬──────┘
       │
       ├─────────────┬──────────────┬──────────────┐
       ▼             ▼              ▼              ▼
   Monitor      Scanner        Updater      Config
   ┌──────┐    ┌──────┐      ┌──────┐    ┌──────┐
   │OpenAI│    │Python│      │ Diff │    │YAML  │
   │Anthr │    │TS/JS │      │Apply │    │Store │
   │Google│    │Swift │      └──────┘    └──────┘
   └──────┘    │Kotlin│
               └──────┘
```

## Components

### 1. Configuration Layer (`config/models.yaml`)

**Purpose**: Central source of truth for all model configurations

**Structure**:
```yaml
providers:      # LLM provider definitions
  openai:
    models:
      chat:
        current: "gpt-4o"
        deprecated: [...]

projects:       # Your applications
  medcore-api:
    path: "/path"
    mappings:   # Where models are used
      - locations: [...]
```

**Why YAML?**
- Human-readable
- Easy to version control
- Supports comments
- Standard format

### 2. Monitor Layer (`monitor/`)

**Purpose**: Check LLM providers for model availability and deprecations

**Classes**:

#### `OpenAIMonitor`
```python
- get_available_models()     # Query API for current models
- check_model_exists(name)   # Verify specific model
- check_deprecations(models) # Detect issues
- suggest_replacements()     # Recommend alternatives
```

#### `AnthropicMonitor`
```python
- test_model(name)           # Test model via API
- check_deprecations(models) # Detect issues
- suggest_replacements()     # Tier-aware recommendations
```

**Design Decisions**:
- **OpenAI**: Uses `/v1/models` endpoint to list all models
- **Anthropic**: No list endpoint, so we test models individually
- **Caching**: Monitors cache results for 15 minutes
- **Error Handling**: Graceful degradation if API unavailable

### 3. Scanner Layer (`scanner/`)

**Purpose**: Find all LLM model references in codebases

**Architecture**:

```
BaseScanner (ABC)
    │
    ├── PythonScanner
    ├── TypeScriptScanner   (planned)
    ├── SwiftScanner        (planned)
    └── KotlinScanner       (planned)
```

#### `BaseScanner` (Abstract)
```python
class BaseScanner:
    MODEL_PATTERNS = [...]           # Regex patterns

    @abstractmethod
    def get_file_extensions() -> List[str]

    @abstractmethod
    def scan_file(path) -> List[ModelReference]

    def scan_project() -> List[ModelReference]
    def extract_model_name(text) -> str
    def generate_report() -> Dict
```

#### `ModelReference` (Data Class)
```python
class ModelReference:
    file_path: str
    line_number: int
    line_content: str
    model_name: str
    context: str          # Variable name or context
    reference_type: str   # "code", "env", "config"
```

**Scanning Strategy**:

1. **File Discovery**: Use `rglob()` to find files by extension
2. **Filtering**: Skip common ignore directories (node_modules, venv, etc.)
3. **Pattern Matching**: Multiple regex patterns for different model name formats
4. **Context Extraction**: Identify variable names, parameter names
5. **Aggregation**: Collect all references into structured format

**Why Multiple Scanners?**
- Different languages have different syntax
- File formats vary (Python: .py, TypeScript: .ts/.tsx, etc.)
- Model references appear differently in each language

### 4. CLI Layer (`cli.py`)

**Purpose**: User-facing interface using Click framework

**Commands**:

```
llm-manager
    ├── monitor [--provider]      Monitor LLM providers
    ├── scan [--project|--path]   Scan codebase
    ├── check --project           Comprehensive check
    ├── list-projects             List configurations
    └── report                    Full status report
```

**UI/UX**:
- Uses **Rich** library for beautiful terminal output
- Tables for structured data
- Color coding: green (ok), yellow (warning), red (error)
- Progress indicators for long operations

### 5. Updater Layer (`updater/`) - Planned

**Purpose**: Generate and apply code updates

**Future Components**:

#### `generate_diff.py`
```python
def generate_update_proposal(
    references: List[ModelReference],
    replacements: Dict[str, str]
) -> UpdateProposal:
    # Create git-style diffs
    # Show before/after
    # Highlight changes
```

#### `apply_updates.py`
```python
def apply_updates(
    proposal: UpdateProposal,
    approved: bool
) -> UpdateResult:
    # Backup files
    # Apply changes
    # Create git commit
    # Generate PR
```

## Data Flow

### Typical "Check" Operation

```
1. User: cli.py check --project medcore-api
           │
2. CLI:    Load config/models.yaml
           │
3. CLI:    Initialize OpenAIMonitor, AnthropicMonitor
           │
4. Monitor: Check providers for model status
           │
5. CLI:    Initialize PythonScanner
           │
6. Scanner: Scan project files for model references
           │
7. CLI:    Compare found models vs provider status
           │
8. CLI:    Generate issues list
           │
9. CLI:    Display results with Rich formatting
```

### Data Structures

```python
# Configuration (from YAML)
Config = {
    'providers': {
        'openai': { 'models': {...} },
        'anthropic': { 'models': {...} }
    },
    'projects': {
        'medcore-api': {
            'path': str,
            'mappings': [
                {
                    'id': str,
                    'provider': str,
                    'locations': [...]
                }
            ]
        }
    }
}

# Scan Results
ScanReport = {
    'total_references': int,
    'by_file': Dict[str, List[ModelReference]],
    'by_model': Dict[str, int],
    'by_type': Dict[str, int]
}

# Check Results
Issue = {
    'severity': 'error' | 'warning',
    'mapping_id': str,
    'file': str,
    'line': int,
    'current_model': str,
    'message': str,
    'suggestions': List[str]
}
```

## Design Patterns

### 1. Strategy Pattern
Different scanners for different languages, all implementing `BaseScanner`

### 2. Factory Pattern
CLI creates appropriate scanner based on project language:
```python
if language == 'python':
    scanner = PythonScanner(path)
elif language == 'typescript':
    scanner = TypeScriptScanner(path)
```

### 3. Template Method
`BaseScanner.scan_project()` defines the algorithm, subclasses implement details

### 4. Data Transfer Object
`ModelReference` encapsulates all information about a found reference

## Extension Points

### Adding a New Provider

1. Create `monitor/check_newprovider.py`:
```python
class NewProviderMonitor:
    def get_available_models(self) -> List[Dict]:
        # Implementation

    def check_deprecations(self, models) -> List[Dict]:
        # Implementation
```

2. Add to `config/models.yaml`:
```yaml
providers:
  newprovider:
    api_endpoint: "..."
    models: {...}
```

3. Import in `cli.py` and add to `monitor` command

### Adding a New Language Scanner

1. Create `scanner/your_language_scanner.py`:
```python
class YourLanguageScanner(BaseScanner):
    def get_file_extensions(self):
        return ['.ext']

    def scan_file(self, file_path):
        # Language-specific scanning
        return references
```

2. Add to CLI scanner factory in `cli.py`

### Adding a New Command

1. Add to `cli.py`:
```python
@cli.command()
@click.option('--your-option')
def your_command(your_option):
    """Your command description"""
    # Implementation
```

## Performance Considerations

### Scanning Large Codebases
- **Skip directories**: Avoids scanning node_modules, venv, etc.
- **Lazy evaluation**: Only read files that match extensions
- **Parallel processing**: Could parallelize file scanning (future)

### API Rate Limits
- **Caching**: Cache provider responses for 15 minutes
- **Batch requests**: Where possible, group API calls
- **Exponential backoff**: Retry with backoff on rate limits

### Memory Usage
- **Streaming**: Read files line-by-line, not all at once
- **Generators**: Use generators for large result sets
- **Cleanup**: Close file handles promptly

## Testing Strategy

```
tests/
├── test_monitors.py       # Test provider monitors
├── test_scanners.py       # Test code scanners
├── test_cli.py            # Test CLI commands
└── fixtures/
    ├── sample_python/     # Test codebases
    ├── sample_typescript/
    └── models.yaml        # Test config
```

## Future Enhancements

1. **Auto-Update**: Generate PRs automatically
2. **Cost Analysis**: Estimate cost savings from model updates
3. **Performance Tracking**: Track model performance metrics
4. **Slack/Discord Integration**: Notifications
5. **Web Dashboard**: Visual interface
6. **CI/CD Plugins**: GitHub Action, GitLab CI
7. **Database Backend**: Track history over time
8. **ML-Powered Suggestions**: Learn from your usage patterns

---

**Want to contribute?** Start with implementing a new scanner or monitor!
