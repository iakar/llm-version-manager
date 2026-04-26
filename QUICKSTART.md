# 🚀 Quick Start Guide

## Installation

```bash
cd /Volumes/Data_Code/llmAgent/llm-version-manager
pip install -r requirements.txt
```

## Setup API Keys

```bash
# Add to your ~/.zshrc or ~/.bashrc
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="..."
```

Or create a `.env` file:

```bash
echo "OPENAI_API_KEY=sk-..." > .env
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
source .env
```

## Basic Commands

### 1. List Your Projects

```bash
python cli.py list-projects
```

This shows all projects configured in `config/models.yaml`:
- Medcore API (Python)
- Medcore UI (TypeScript)
- Incluve iOS (Swift)
- Incluve Android (Kotlin)

### 2. Scan a Project

Find all LLM model references in your code:

```bash
python cli.py scan --project medcore-api
```

Output shows:
- Total model references found
- Which models are used and how many times
- Detailed file locations (optional)

### 3. Monitor Providers

Check if your models are still valid:

```bash
# Check all providers
python cli.py monitor

# Check specific provider
python cli.py monitor --provider openai
python cli.py monitor --provider anthropic
```

This tells you:
- Which models are available
- Which models are deprecated
- Warnings about models you're using

### 4. Comprehensive Check

Combines scanning + monitoring to find issues:

```bash
python cli.py check --project medcore-api
```

This will:
- ✅ Validate all models in your project
- ⚠️ Warn about deprecated models
- 💡 Suggest replacements

### 5. Generate Report

Full status across all providers and projects:

```bash
python cli.py report
```

## Example Workflow

### Scenario: You want to ensure Medcore API is using current models

```bash
# 1. Check what models you're using
python cli.py scan --project medcore-api

# 2. Validate them against provider APIs
python cli.py check --project medcore-api

# 3. If issues found, check suggestions
python cli.py monitor --provider openai

# 4. Update models.yaml if needed

# 5. Re-check
python cli.py check --project medcore-api
```

## Daily Usage

Add this to your cron or GitHub Actions:

```bash
#!/bin/bash
# check-models.sh

echo "🤖 Checking LLM models..."

python cli.py check --project medcore-api
python cli.py check --project medcore-ui
python cli.py check --project incluve-ios
python cli.py check --project incluve-android

if [ $? -ne 0 ]; then
  echo "⚠️  Issues found. Please review and update."
fi
```

## Customization

### Add a New Project

Edit `config/models.yaml`:

```yaml
projects:
  my-new-app:
    name: "My New App"
    path: "/path/to/app"
    language: "python"
    mappings:
      - id: "my-app-chat"
        purpose: "chat"
        provider: "openai"
        tier: "current"
        locations:
          - type: "code"
            file: "config.py"
            line_number: 10
```

### Change Model Versions

Update in `config/models.yaml` under `providers`:

```yaml
providers:
  openai:
    models:
      chat:
        current: "gpt-4o-2024-11-20"  # Update this
```

## Troubleshooting

### "API key not found"
Set environment variables:
```bash
export OPENAI_API_KEY="your-key"
```

### "Project not found"
Check spelling in `config/models.yaml` or use:
```bash
python cli.py list-projects
```

### "Scanner not implemented"
Currently supports Python. TypeScript, Swift, Kotlin scanners coming soon.

## Next Steps

1. ✅ Run initial scan of your projects
2. ✅ Fix any deprecated models found
3. ✅ Add to CI/CD pipeline
4. ✅ Schedule daily monitoring
5. ✅ Customize for your needs

---

**Need help?** Check README.md or open an issue.
