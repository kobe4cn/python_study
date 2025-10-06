"""Pytest configuration file"""

import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "integration: Mark integration tests (requires network or external services)"
    )
    config.addinivalue_line("markers", "slow: Mark slow tests")
    config.addinivalue_line("markers", "unit: Mark unit tests")
    config.addinivalue_line("markers", "api: Mark API tests")
    config.addinivalue_line("markers", "llm: Mark LLM-related tests")


@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture"""
    from core.config import AppSettings

    return AppSettings(
        environment="development",
        debug=True,
        llm_provider="qwen",
        llm_model="qwen3-max",
        llm_api_key="test-api-key",
        llm_base_url="https://test.example.com",
        database_url="sqlite:///:memory:",
    )


@pytest.fixture(scope="function")
def test_container(test_config):
    """Test container fixture"""
    from core.container import Container

    container = Container(test_config)
    yield container
    container.reset()


@pytest.fixture
def mock_llm():
    """Mock LLM fixture"""
    from llm.base import BaseLlmModel

    class MockLLM(BaseLlmModel):
        def llm_json_response(self, system_prompt: str, human_prompt: str):
            return '{"result": "test"}'

        def llm_chat_response(self, system_prompt: str, human_prompt: str):
            return "Test response"

        def llm_chat_response_by_human_prompt(self, human_prompt: str):
            return "Test response"

    return MockLLM()


@pytest.fixture
def sample_documents():
    """Sample documents fixture"""
    from langchain_core.documents import Document

    return [
        Document(
            page_content="This is the content of the first test document.",
            metadata={"source": "test1.txt", "type": "test"},
        ),
        Document(
            page_content="This is the content of the second test document.",
            metadata={"source": "test2.txt", "type": "test"},
        ),
    ]


@pytest.fixture
def temp_upload_dir(tmp_path):
    """Temporary upload directory fixture"""
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    return upload_dir
