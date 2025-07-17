"""
Shared utilities for test files.
"""

from colorama import init, Fore, Style
from pathlib import Path
import json
from typing import Dict, Any, Optional, Set
from datetime import datetime

# Initialize colorama
init()


def get_timestamp() -> str:
    """Get current timestamp in a readable format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


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


class TestResult:
    def __init__(self, name: str, passed: bool, error: Optional[str] = None):
        self.name = name
        self.passed = passed
        self.error = error

    def __str__(self) -> str:
        emoji = "✅" if self.passed else "❌"
        result = f"{emoji} {self.name}"
        if self.error:
            result += f" - Error: {self.error}"
        return result


class TestSession:
    """Tracks resources created during a test session."""

    def __init__(self):
        self.created_canvas_ids: Set[str] = set()
        self.user_id: Optional[int] = None
        self.token_id: Optional[str] = None

    def track_canvas(self, canvas_id: str) -> None:
        """Track a canvas created during testing."""
        self.created_canvas_ids.add(canvas_id)
        print_info(f"{get_timestamp()} Tracking test canvas: {canvas_id}")
