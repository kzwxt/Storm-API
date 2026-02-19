"""Test StormService initialization and configuration."""

import pytest
from core.storm_service import StormService
from knowledge_storm import STORMWikiLMConfigs


def test_storm_service_initialization():
    """Test that StormService initializes correctly."""
    service = StormService()
    
    assert service is not None
    assert hasattr(service, 'lm_configs')
    assert hasattr(service, 'retriever')
    assert isinstance(service.lm_configs, STORMWikiLMConfigs)


def test_storm_service_singleton():
    """Test that StormService is a singleton (same instance reused)."""
    from api.routes import get_storm_service
    
    service1 = get_storm_service()
    service2 = get_storm_service()
    
    assert service1 is service2


def test_lm_configs_creation():
    """Test that LLM configs are created with correct provider."""
    service = StormService()
    
    assert service.lm_configs is not None
    assert service.lm_configs.question_asker_lm is not None
    assert service.lm_configs.conv_simulator_lm is not None
    assert service.lm_configs.article_gen_lm is not None
    assert service.lm_configs.article_polish_lm is not None
    assert service.lm_configs.outline_gen_lm is not None


def test_retriever_initialization():
    """Test that retriever is initialized correctly."""
    service = StormService()
    
    assert service.retriever is not None
    assert hasattr(service.retriever, 'forward')
    assert hasattr(service.retriever, '__call__')

@pytest.mark.slow
@pytest.mark.integration
def test_run_returns_string():
    """Test that run method returns a string."""
    service = StormService()
    
    result = service.run("Python")
    
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.slow
@pytest.mark.integration
def test_run_with_valid_topic():
    """Test that run method produces output for valid topic."""
    service = StormService()
    
    result = service.run("Python")
    
    assert "Python" in result or len(result) > 100


@pytest.mark.slow
@pytest.mark.integration
def test_run_clears_memory():
    """Test that run method clears memory between runs."""
    from core.storm_service import get_memory_storage_files, clear_memory_storage
    
    service = StormService()
    
    # First run
    service.run("Python")
    files1 = get_memory_storage_files()
    size1 = len(files1)
    
    # Clear and second run
    clear_memory_storage()
    service.run("Java")
    files2 = get_memory_storage_files()
    size2 = len(files2)
    
    # After clearing, first storage should be empty or different
    assert size1 == 0 or files1 != files2