import os
import sys
from pathlib import Path
import pytest

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.studypilot.memory.store import MemoryStore
from src.studypilot.tools.registry import get_default_registry

@pytest.fixture
def temp_db_path(tmp_path):
    return str(tmp_path / "test_studypilot.db")

@pytest.fixture
def memory_store(temp_db_path):
    return MemoryStore(db_path=temp_db_path)

@pytest.fixture
def tool_registry():
    return get_default_registry()
