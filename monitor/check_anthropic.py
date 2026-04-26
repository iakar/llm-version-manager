"""
Anthropic Model Monitor
Checks Anthropic API for current models and deprecation notices
"""
import os
from typing import Dict, List, Optional
from datetime import datetime
import requests


class AnthropicMonitor:
    """Monitor Anthropic Claude models for changes and deprecations"""

    # Known Anthropic models (API doesn't provide a list endpoint)
    KNOWN_MODELS = {
        "chat": {
            "current": [
                "claude-sonnet-4-20250514",
                "claude-sonnet-4-6",
                "claude-3-7-sonnet-20250219",
                "claude-3-7-sonnet-latest",
                "claude-3-5-haiku-20241022",
                "claude-3-5-haiku-latest",
                "claude-3-5-sonnet-20241022",
                "claude-3-5-sonnet-20240620",
            ],
            "deprecated": [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
                "claude-2.1",
                "claude-2.0",
            ]
        }
    }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = "https://api.anthropic.com/v1"

    def test_model(self, model_name: str) -> bool:
        """
        Test if a model exists by making a minimal API call
        This is a workaround since Anthropic doesn't have a /models endpoint
        """
        if not self.api_key:
            raise ValueError("Anthropic API key not found")

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        payload = {
            "model": model_name,
            "max_tokens": 1,
            "messages": [
                {"role": "user", "content": "Hi"}
            ]
        }

        try:
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload,
                timeout=10
            )

            # If we get a 200 or the model_name appears in error, it exists
            if response.status_code == 200:
                return True

            # Check error message
            if response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "")
                # If error is about model not existing, return False
                if "model" in error_msg.lower() and "not found" in error_msg.lower():
                    return False
                # Other errors (rate limit, invalid params) suggest model exists
                return True

            return False

        except Exception as e:
            print(f"Error testing model {model_name}: {e}")
            return False

    def get_chat_models(self) -> List[str]:
        """Get all known chat models"""
        return self.KNOWN_MODELS["chat"]["current"]

    def get_deprecated_models(self) -> List[str]:
        """Get all known deprecated models"""
        return self.KNOWN_MODELS["chat"]["deprecated"]

    def check_model_exists(self, model_name: str) -> bool:
        """Check if a specific model exists"""
        # First check known models list
        all_known = self.KNOWN_MODELS["chat"]["current"] + self.KNOWN_MODELS["chat"]["deprecated"]
        if model_name in all_known:
            # For known deprecated models, mark as not existing
            if model_name in self.KNOWN_MODELS["chat"]["deprecated"]:
                return False
            return True

        # If not in known list, test via API
        return self.test_model(model_name)

    def check_deprecations(self, current_models: Dict[str, str]) -> List[Dict]:
        """
        Check if any of the current models are deprecated

        Args:
            current_models: Dict of purpose -> model_name

        Returns:
            List of deprecation warnings
        """
        warnings = []

        for purpose, model_name in current_models.items():
            # Check if model is in deprecated list
            if model_name in self.KNOWN_MODELS["chat"]["deprecated"]:
                warnings.append({
                    "purpose": purpose,
                    "model": model_name,
                    "status": "deprecated",
                    "message": f"Model '{model_name}' is deprecated",
                    "severity": "high",
                    "timestamp": datetime.now().isoformat()
                })
            # Check if model exists at all
            elif not self.check_model_exists(model_name):
                warnings.append({
                    "purpose": purpose,
                    "model": model_name,
                    "status": "not_found",
                    "message": f"Model '{model_name}' not found in Anthropic API",
                    "severity": "high",
                    "timestamp": datetime.now().isoformat()
                })

        return warnings

    def suggest_replacements(self, deprecated_model: str) -> List[str]:
        """Suggest replacement models for a deprecated model"""
        suggestions = []

        # Map old models to new ones
        replacements = {
            "claude-3-opus": ["claude-sonnet-4-20250514", "claude-sonnet-4-6"],
            "claude-3-sonnet-20240229": ["claude-3-7-sonnet-20250219"],
            "claude-3-haiku-20240307": ["claude-3-5-haiku-20241022"],
            "claude-2": ["claude-3-7-sonnet-20250219"],
        }

        for old_pattern, new_models in replacements.items():
            if old_pattern in deprecated_model:
                suggestions.extend(new_models)

        # If no specific replacement, suggest latest models by tier
        if not suggestions:
            if "opus" in deprecated_model.lower():
                suggestions = ["claude-sonnet-4-20250514"]
            elif "sonnet" in deprecated_model.lower():
                suggestions = ["claude-3-7-sonnet-20250219"]
            elif "haiku" in deprecated_model.lower():
                suggestions = ["claude-3-5-haiku-20241022"]
            else:
                suggestions = ["claude-sonnet-4-20250514"]

        return suggestions

    def get_tier_recommendation(self, use_case: str) -> str:
        """Recommend a model tier based on use case"""
        use_case_lower = use_case.lower()

        if any(word in use_case_lower for word in ["simple", "translation", "basic"]):
            return "claude-3-5-haiku-20241022"
        elif any(word in use_case_lower for word in ["medium", "generation", "categorization"]):
            return "claude-3-7-sonnet-20250219"
        elif any(word in use_case_lower for word in ["complex", "reasoning", "conversation"]):
            return "claude-sonnet-4-20250514"
        else:
            return "claude-3-7-sonnet-20250219"  # Default to standard

    def generate_report(self) -> Dict:
        """Generate a comprehensive report of Anthropic models"""
        return {
            "provider": "anthropic",
            "timestamp": datetime.now().isoformat(),
            "current_models": self.get_chat_models(),
            "deprecated_models": self.get_deprecated_models(),
            "total_current": len(self.get_chat_models()),
            "total_deprecated": len(self.get_deprecated_models())
        }


if __name__ == "__main__":
    # Test the monitor
    monitor = AnthropicMonitor()

    print("=== Anthropic Model Monitor ===\n")

    print("Current Models:")
    for model in monitor.get_chat_models():
        print(f"  ✅ {model}")

    print("\nDeprecated Models:")
    for model in monitor.get_deprecated_models():
        print(f"  ❌ {model}")

    # Test deprecation check
    print("\n=== Checking Test Models ===")
    test_models = {
        "chat-light": "claude-3-5-haiku-20241022",  # Current
        "chat-old": "claude-2.1",  # Deprecated
        "chat-fake": "claude-99-ultra"  # Doesn't exist
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
