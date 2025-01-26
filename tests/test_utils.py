"""
Shared utilities for test files.
"""

from colorama import init, Fore, Style
from pathlib import Path
import json
from typing import Dict, Any

# Initialize colorama
init()

def print_success(message: str) -> None:
    """Print a success message in green with checkmark."""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")

def print_error(message: str) -> None:
    """Print an error message in red with cross."""
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")

def print_info(message: str) -> None:
    """Print an info message in blue with info symbol."""
    print(f"{Fore.BLUE}ℹ️ {message}{Style.RESET_ALL}")

def print_warning(message: str) -> None:
    """Print a warning message in yellow with warning symbol."""
    print(f"{Fore.YELLOW}⚠️ {message}{Style.RESET_ALL}")

def print_header(message: str) -> None:
    """Print a header in cyan with separator."""
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"🔍 {message}")
    print(f"{'='*50}{Style.RESET_ALL}")

def load_config() -> Dict[str, Any]:
    """Load configuration from config.json file."""
    config_path = Path(__file__).parent / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(
            "config.json not found. Please create it with your API credentials."
        )
    
    with open(config_path) as f:
        return json.load(f) 