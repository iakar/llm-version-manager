# Contributing to LLM Version Manager

First off, thanks for taking the time to contribute! 🎉

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps to reproduce the problem
* Provide specific examples
* Describe the behavior you observed and what you expected
* Include your environment details (OS, Python version, etc.)

### Suggesting Features

Feature suggestions are welcome! Please provide:

* A clear and descriptive title
* A detailed description of the proposed feature
* Examples of how it would be used
* Why this feature would be useful

### Pull Requests

1. Fork the repo
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (when available)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/llm-version-manager.git
cd llm-version-manager

# Install dependencies
pip install -r requirements.txt

# Set up API keys for testing
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Run the tool
python cli.py --help
```

## Coding Standards

* Follow PEP 8 style guide for Python
* Use meaningful variable and function names
* Add docstrings to functions and classes
* Keep functions focused and small
* Write clear commit messages

## Adding a New Language Scanner

1. Create `scanner/your_language_scanner.py`:

```python
from .base_scanner import BaseScanner, ModelReference

class YourLanguageScanner(BaseScanner):
    def get_file_extensions(self):
        return ['.ext']

    def scan_file(self, file_path):
        # Your implementation
        pass
```

2. Add tests in `tests/test_your_language_scanner.py`
3. Update CLI in `cli.py`
4. Update documentation

## Adding a New Provider Monitor

1. Create `monitor/check_yourprovider.py`:

```python
class YourProviderMonitor:
    def __init__(self, api_key=None):
        # Initialize
        pass

    def get_available_models(self):
        # Implementation
        pass

    def check_deprecations(self, models):
        # Implementation
        pass
```

2. Add to `config/models.yaml`
3. Update CLI commands
4. Add tests

## Project Structure

```
llm-version-manager/
├── cli.py              # Main CLI interface
├── config/             # Configuration files
├── monitor/            # Provider monitors
├── scanner/            # Code scanners
├── updater/            # Update logic (future)
└── tests/              # Test suite
```

## Testing

```bash
# Run tests (when available)
pytest tests/

# Run specific test
pytest tests/test_scanner.py

# Run with coverage
pytest --cov=. tests/
```

## Documentation

* Update README.md for user-facing changes
* Update ARCHITECTURE.md for design changes
* Add examples to QUICKSTART.md
* Update ROADMAP.md if changing plans

## Code Review Process

1. All PRs require review before merging
2. Address review comments
3. Ensure CI passes (when set up)
4. Maintain clean commit history

## Community

* Be respectful and inclusive
* Help others learn
* Give constructive feedback
* Celebrate contributions

## Questions?

* Open an issue with your question
* Check existing documentation
* Look at closed issues/PRs for examples

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing!** 🚀
