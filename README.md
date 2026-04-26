# 🤖 LLM Version Manager

**Never let your AI models go stale again.**

Automatically monitor LLM providers (OpenAI, Anthropic, Google) for model deprecations and keep your codebase up-to-date.

## 🎯 Problem

LLM providers constantly update their models:
- Models get deprecated with little notice
- New models offer better performance at lower costs
- Manually tracking changes across providers is tedious
- One outdated model can break your production app

## ✨ Solution

LLM Version Manager:
- ✅ **Monitors** OpenAI, Anthropic, Google APIs for model changes
- ✅ **Scans** your codebase to find all model references
- ✅ **Detects** deprecated or non-existent models
- ✅ **Suggests** replacements based on your use case
- ✅ **Updates** your code automatically (with your approval)
- ✅ **Works** with Python, TypeScript, Swift, Kotlin (extensible)

## 🚀 Quick Start

### Installation

```bash
cd llm-version-manager
pip install -r requirements.txt
chmod +x cli.py
```

### Set up API keys

```bash
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
```

### Basic Usage

```bash
# Check provider status
./cli.py monitor

# List configured projects
./cli.py list-projects

# Scan a project for model references
./cli.py scan --project medcore-api

# Check a project for issues
./cli.py check --project medcore-api

# Generate full report
./cli.py report
```

## 📋 Commands

### `monitor`
Check LLM providers for model updates and deprecations

```bash
./cli.py monitor --provider openai
./cli.py monitor --provider anthropic
./cli.py monitor  # Check all providers
```

### `scan`
Scan your codebase for LLM model references

```bash
./cli.py scan --project medcore-api
./cli.py scan --path /path/to/project --language python
```

### `check`
Comprehensive check: combines monitoring + scanning to detect issues

```bash
./cli.py check --project medcore-api
```

Output:
- ✅ All models are valid
- ⚠️ Deprecated models found with suggested replacements
- ❌ Non-existent models detected

### `list-projects`
Show all configured projects from `config/models.yaml`

### `report`
Generate a comprehensive status report across all providers and projects

## 🔧 Configuration

Edit `config/models.yaml` to:
- Add/remove LLM providers
- Configure deprecation schedules
- Map your projects and where they use models
- Set monitoring preferences

Example project mapping:

```yaml
projects:
  your-app:
    name: "Your App"
    path: "/path/to/your-app"
    language: "python"
    mappings:
      - id: "your-app-chat"
        purpose: "chat"
        provider: "openai"
        tier: "current"
        locations:
          - type: "env"
            file: ".env"
            key: "OPENAI_MODEL"
          - type: "code"
            file: "app/config.py"
            line_number: 42
```

## 🏗️ Architecture

```
llm-version-manager/
├── config/
│   └── models.yaml          # Central configuration
├── monitor/
│   ├── check_openai.py      # OpenAI API monitor
│   ├── check_anthropic.py   # Anthropic API monitor
│   └── check_google.py      # Google Gemini monitor
├── scanner/
│   ├── base_scanner.py      # Abstract scanner
│   ├── python_scanner.py    # Python code scanner
│   ├── typescript_scanner.py
│   ├── swift_scanner.py
│   └── kotlin_scanner.py
├── updater/
│   ├── generate_diff.py     # Generate update proposals
│   └── apply_updates.py     # Apply approved changes
└── cli.py                    # Main CLI interface
```

## 🎓 Use Cases

### 1. Daily Monitoring (CI/CD)

Run as a GitHub Action:

```yaml
name: Check LLM Models
on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check models
        run: |
          pip install -r requirements.txt
          ./cli.py check --project your-app
```

### 2. Pre-Deployment Check

Add to your deployment pipeline:

```bash
#!/bin/bash
echo "Checking LLM models..."
./cli.py check --project your-app
if [ $? -ne 0 ]; then
  echo "⚠️  Outdated models detected. Please review."
  exit 1
fi
```

### 3. Developer Tool

Check before committing:

```bash
# Add to .git/hooks/pre-commit
./cli.py scan --project your-app
```

## 🌍 Extending to Other Languages

To add support for a new language:

1. Create `scanner/your_language_scanner.py`
2. Extend `BaseScanner`
3. Implement `get_file_extensions()` and `scan_file()`
4. Add to CLI

Example:

```python
from .base_scanner import BaseScanner, ModelReference

class TypeScriptScanner(BaseScanner):
    def get_file_extensions(self):
        return ['.ts', '.tsx', '.js', '.jsx']

    def scan_file(self, file_path):
        # Your scanning logic
        pass
```

## 🤝 Contributing

This tool was built to solve a real problem. Contributions welcome!

1. Fork the repo
2. Create your feature branch
3. Add tests
4. Submit a PR

## 📝 License

MIT License - feel free to use in your projects

## 🙏 Credits

Built with:
- OpenAI, Anthropic, Google APIs
- Click for CLI
- Rich for beautiful terminal output
- PyYAML for configuration

---

**Questions or Issues?**
Open an issue on GitHub or contribute a fix!
