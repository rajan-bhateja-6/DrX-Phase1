"""
Model configuration for DrX-Phase1 application.
This module provides centralized configuration for model clients and API settings.
"""

import os
from typing import Optional
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ModelConfig:
    """Configuration class for model clients and API settings."""

    def __init__(self):
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
        self.default_model: str = "gpt-4o"
        self.max_tokens: int = 40000
        self.temperature: float = 0.4

    def validate_config(self) -> bool:
        """Validate that required configuration is present."""
        if not self.openai_api_key:
            print("ERROR: OPENAI_API_KEY is required but not found in environment variables")
            print("Please create a .env file in the project root with your API key:")
            print("OPENAI_API_KEY=your_actual_api_key_here")
            print("GROQ_API_KEY=your_groq_api_key_here")
            raise ValueError("OPENAI_API_KEY is required but not found in environment variables")
        return True

    def get_model_client(self) -> OpenAIChatCompletionClient:
        """Get configured OpenAI model client."""
        self.validate_config()
        return OpenAIChatCompletionClient(
            model=self.default_model,
            api_key=self.openai_api_key
        )

    def get_api_key(self) -> str:
        """Get OpenAI API key."""
        self.validate_config()
        return self.openai_api_key


# Global configuration instance
config = ModelConfig()
