"""
Base Scanner
Abstract base class for language-specific code scanners
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from pathlib import Path
import re


class ModelReference:
    """Represents a model reference found in code"""

    def __init__(
        self,
        file_path: str,
        line_number: int,
        line_content: str,
        model_name: str,
        context: str = "",
        reference_type: str = "code"  # code, env, config
    ):
        self.file_path = file_path
        self.line_number = line_number
        self.line_content = line_content
        self.model_name = model_name
        self.context = context
        self.reference_type = reference_type

    def to_dict(self) -> Dict:
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "line_content": self.line_content,
            "model_name": self.model_name,
            "context": self.context,
            "reference_type": self.reference_type
        }

    def __repr__(self):
        return f"ModelReference({self.file_path}:{self.line_number} -> {self.model_name})"


class BaseScanner(ABC):
    """Base class for code scanners"""

    # Common model name patterns across all providers
    MODEL_PATTERNS = [
        # OpenAI
        r'gpt-[\w\.-]+',
        r'whisper-\d+',
        r'text-embedding-[\w\.-]+',
        r'davinci-[\w\.-]+',

        # Anthropic
        r'claude-[\w\.-]+',

        # Google
        r'gemini-[\w\.-]+',
        r'palm-[\w\.-]+',

        # Generic patterns
        r'[\w-]+-\d{4}-\d{2}-\d{2}',  # Date-based versions
    ]

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        if not self.project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")

    @abstractmethod
    def get_file_extensions(self) -> List[str]:
        """Return list of file extensions to scan (e.g., ['.py', '.pyi'])"""
        pass

    @abstractmethod
    def scan_file(self, file_path: Path) -> List[ModelReference]:
        """Scan a single file for model references"""
        pass

    def scan_project(self) -> List[ModelReference]:
        """Scan entire project for model references"""
        all_references = []

        extensions = self.get_file_extensions()

        for ext in extensions:
            for file_path in self.project_path.rglob(f"*{ext}"):
                # Skip common directories to ignore
                if self._should_skip_path(file_path):
                    continue

                try:
                    references = self.scan_file(file_path)
                    all_references.extend(references)
                except Exception as e:
                    print(f"Error scanning {file_path}: {e}")

        return all_references

    def _should_skip_path(self, path: Path) -> bool:
        """Check if path should be skipped"""
        skip_dirs = {
            'node_modules', 'venv', 'env', '.env', '__pycache__',
            '.git', 'dist', 'build', '.next', 'target',
            'Pods', 'DerivedData', '.gradle'
        }

        # Check if any parent directory is in skip list
        for parent in path.parents:
            if parent.name in skip_dirs:
                return True

        return False

    def extract_model_name(self, text: str) -> Optional[str]:
        """Extract model name from text using common patterns"""
        for pattern in self.MODEL_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None

    def scan_env_file(self, file_path: Path) -> List[ModelReference]:
        """Scan .env file for model references"""
        references = []

        if not file_path.exists():
            return references

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue

                    # Look for model-related env vars
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")

                        # Check if this is a model configuration
                        if any(x in key.upper() for x in ['MODEL', 'ENGINE']):
                            model_name = self.extract_model_name(value)
                            if model_name:
                                references.append(ModelReference(
                                    file_path=str(file_path),
                                    line_number=line_num,
                                    line_content=line,
                                    model_name=model_name,
                                    context=key,
                                    reference_type="env"
                                ))
        except Exception as e:
            print(f"Error scanning env file {file_path}: {e}")

        return references

    def generate_report(self, references: List[ModelReference]) -> Dict:
        """Generate a report from found references"""
        report = {
            "total_references": len(references),
            "by_file": {},
            "by_model": {},
            "by_type": {}
        }

        for ref in references:
            # By file
            if ref.file_path not in report["by_file"]:
                report["by_file"][ref.file_path] = []
            report["by_file"][ref.file_path].append(ref.to_dict())

            # By model
            if ref.model_name not in report["by_model"]:
                report["by_model"][ref.model_name] = 0
            report["by_model"][ref.model_name] += 1

            # By type
            if ref.reference_type not in report["by_type"]:
                report["by_type"][ref.reference_type] = 0
            report["by_type"][ref.reference_type] += 1

        return report
