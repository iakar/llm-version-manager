"""
OpenAI Model Monitor
Checks OpenAI API for current models and deprecation notices
"""
import os
from typing import Dict, List, Optional
from datetime import datetime
import requests


class OpenAIMonitor:
    """Monitor OpenAI models for changes and deprecations"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"

    def get_available_models(self) -> List[Dict]:
        """Fetch all available models from OpenAI API"""
        if not self.api_key:
            raise ValueError("OpenAI API key not found")

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = requests.get(f"{self.base_url}/models", headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            print(f"Error fetching OpenAI models: {e}")
            return []

    def check_model_exists(self, model_name: str) -> bool:
        """Check if a specific model exists"""
        models = self.get_available_models()
        model_ids = [m["id"] for m in models]
        return model_name in model_ids

    def get_chat_models(self) -> List[str]:
        """Get all available chat models"""
        models = self.get_available_models()
        chat_models = [
            m["id"] for m in models
            if "gpt" in m["id"].lower() and "instruct" not in m["id"].lower()
        ]
        return sorted(chat_models, reverse=True)

    def get_embedding_models(self) -> List[str]:
        """Get all available embedding models"""
        models = self.get_available_models()
        embedding_models = [
            m["id"] for m in models
            if "embedding" in m["id"].lower()
        ]
        return sorted(embedding_models, reverse=True)

    def get_whisper_models(self) -> List[str]:
        """Get all available Whisper (transcription) models"""
        models = self.get_available_models()
        whisper_models = [
            m["id"] for m in models
            if "whisper" in m["id"].lower()
        ]
        return sorted(whisper_models, reverse=True)

    def check_deprecations(self, current_models: Dict[str, str]) -> List[Dict]:
        """
        Check if any of the current models are deprecated or don't exist

        Args:
            current_models: Dict of purpose -> model_name

        Returns:
            List of deprecation warnings
        """
        warnings = []
        available_models = self.get_available_models()
        model_ids = [m["id"] for m in available_models]

        for purpose, model_name in current_models.items():
            if model_name not in model_ids:
                warnings.append({
                    "purpose": purpose,
                    "model": model_name,
                    "status": "not_found",
                    "message": f"Model '{model_name}' not found in OpenAI API",
                    "severity": "high",
                    "timestamp": datetime.now().isoformat()
                })

        return warnings

    def suggest_replacements(self, deprecated_model: str) -> List[str]:
        """Suggest replacement models for a deprecated model"""
        suggestions = []

        # Map old models to new ones
        replacements = {
            "gpt-4-turbo": ["gpt-4o-2024-11-20", "gpt-4o"],
            "gpt-3.5-turbo": ["gpt-4o-mini"],
            "text-embedding-ada-002": ["text-embedding-3-small", "text-embedding-3-large"],
        }

        for old_pattern, new_models in replacements.items():
            if old_pattern in deprecated_model:
                suggestions.extend(new_models)

        # If no specific replacement, suggest latest models
        if not suggestions:
            if "gpt" in deprecated_model:
                suggestions = ["gpt-4o-2024-11-20", "gpt-4o-mini"]
            elif "embedding" in deprecated_model:
                suggestions = ["text-embedding-3-small"]
            elif "whisper" in deprecated_model:
                suggestions = ["whisper-1"]

        return suggestions

    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get detailed information about a specific model"""
        models = self.get_available_models()
        for model in models:
            if model["id"] == model_name:
                return model
        return None

    def generate_report(self) -> Dict:
        """Generate a comprehensive report of OpenAI models"""
        return {
            "provider": "openai",
            "timestamp": datetime.now().isoformat(),
            "chat_models": self.get_chat_models(),
            "embedding_models": self.get_embedding_models(),
            "whisper_models": self.get_whisper_models(),
            "total_models": len(self.get_available_models())
        }


if __name__ == "__main__":
    # Test the monitor
    monitor = OpenAIMonitor()

    print("=== OpenAI Model Monitor ===\n")

    print("Chat Models:")
    for model in monitor.get_chat_models()[:10]:  # Show top 10
        print(f"  - {model}")

    print("\nEmbedding Models:")
    for model in monitor.get_embedding_models():
        print(f"  - {model}")

    print("\nWhisper Models:")
    for model in monitor.get_whisper_models():
        print(f"  - {model}")

    # Test deprecation check
    print("\n=== Checking Test Models ===")
    test_models = {
        "chat": "gpt-5.4-nano",  # This doesn't exist
        "embedding": "text-embedding-3-small"  # This exists
    }

    warnings = monitor.check_deprecations(test_models)
    if warnings:
        print("\n⚠️  Warnings:")
        for warning in warnings:
            print(f"  - {warning['message']}")
            suggestions = monitor.suggest_replacements(warning['model'])
            if suggestions:
                print(f"    Suggested replacements: {', '.join(suggestions)}")
    else:
        print("\n✅ All models are valid")
