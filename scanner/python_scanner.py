"""
Python Code Scanner
Scans Python files for LLM model references
"""
from pathlib import Path
from typing import List
import re

from .base_scanner import BaseScanner, ModelReference


class PythonScanner(BaseScanner):
    """Scanner for Python codebases"""

    def get_file_extensions(self) -> List[str]:
        return ['.py', '.pyi']

    def scan_file(self, file_path: Path) -> List[ModelReference]:
        """Scan a Python file for model references"""
        references = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    # Skip comments
                    if line.strip().startswith('#'):
                        continue

                    # Look for model names in various contexts
                    found_models = self._find_models_in_line(line)

                    for model_name, context in found_models:
                        references.append(ModelReference(
                            file_path=str(file_path.relative_to(self.project_path)),
                            line_number=line_num,
                            line_content=line.strip(),
                            model_name=model_name,
                            context=context
                        ))

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

        return references

    def _find_models_in_line(self, line: str) -> List[tuple]:
        """Find all model references in a line"""
        found = []

        # Pattern 1: String literals with model names
        # e.g., model="gpt-4o", engine='claude-3', OPENAI_MODEL = "gpt-4o-mini"
        string_pattern = r'["\']([^"\']*(?:gpt|claude|gemini|whisper|embedding|palm)[^"\']*)["\']'
        for match in re.finditer(string_pattern, line, re.IGNORECASE):
            potential_model = match.group(1)
            model_name = self.extract_model_name(potential_model)
            if model_name:
                # Try to get context (variable name or parameter)
                context_match = re.search(r'(\w+)\s*=\s*["\']', line[:match.start()])
                context = context_match.group(1) if context_match else "string literal"
                found.append((model_name, context))

        # Pattern 2: Environment variable defaults
        # e.g., os.getenv('MODEL', 'gpt-4o')
        env_pattern = r'getenv\(["\'][\w_]+["\']\s*,\s*["\']([^"\']+)["\']\)'
        for match in re.finditer(env_pattern, line):
            default_value = match.group(1)
            model_name = self.extract_model_name(default_value)
            if model_name:
                found.append((model_name, "getenv default"))

        # Pattern 3: F-strings and format strings
        # e.g., f"model: {MODEL}" where MODEL might be defined elsewhere
        # We'll catch the constant name for manual review

        return found

    def scan_project(self) -> List[ModelReference]:
        """Scan Python project including .env files"""
        references = super().scan_project()

        # Also scan .env files
        for env_file in self.project_path.rglob('.env*'):
            if env_file.is_file() and not env_file.name.endswith('.example'):
                env_refs = self.scan_env_file(env_file)
                references.extend(env_refs)

        return references


if __name__ == "__main__":
    # Test the scanner
    import sys

    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "/Volumes/Data_Code/medcore_api"

    print(f"Scanning Python project: {project_path}\n")

    scanner = PythonScanner(project_path)
    references = scanner.scan_project()

    print(f"Found {len(references)} model references:\n")

    for ref in references:
        print(f"{ref.file_path}:{ref.line_number}")
        print(f"  Model: {ref.model_name}")
        print(f"  Context: {ref.context}")
        print(f"  Line: {ref.line_content[:80]}...")
        print()

    # Generate report
    report = scanner.generate_report(references)
    print("\n=== Summary ===")
    print(f"Total references: {report['total_references']}")
    print(f"\nModels found:")
    for model, count in report['by_model'].items():
        print(f"  {model}: {count} occurrences")
