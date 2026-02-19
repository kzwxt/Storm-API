"""Test in-memory storage functionality."""

import pytest
from knowledge_storm.utils import FileIOHelper

# Import storm_service to activate FileIOHelper override
import core.storm_service
from core.storm_service import (
    get_memory_storage_files,
    get_memory_storage_size,
    clear_memory_storage
)


def test_memory_storage_is_empty_initially():
    """Test that memory storage is empty initially."""
    clear_memory_storage()
    files = get_memory_storage_files()
    
    assert len(files) == 0


def test_memory_storage_write_and_read():
    """Test that data can be written to and read from memory."""
    clear_memory_storage()
    
    # Write data with full path (STORM uses full paths)
    FileIOHelper.write_str("Hello, World!", "test/test.txt")
    
    # Read data
    content = FileIOHelper.read_str("test/test.txt")
    
    assert content == "Hello, World!"


def test_memory_storage_multiple_files():
    """Test that multiple files can be stored in memory."""
    clear_memory_storage()
    
    # Write multiple files
    FileIOHelper.write_str("Content 1", "test/file1.txt")
    FileIOHelper.write_str("Content 2", "test/file2.txt")
    FileIOHelper.write_str("Content 3", "test/file3.txt")
    
    # Check storage size
    size = get_memory_storage_size()
    
    assert size == 3


def test_memory_storage_clear():
    """Test that memory storage can be cleared."""
    clear_memory_storage()
    
    # Write data
    FileIOHelper.write_str("Test content", "test/test.txt")
    
    # Verify data exists
    assert get_memory_storage_size() == 1
    
    # Clear storage
    clear_memory_storage()
    
    # Verify data is gone
    assert get_memory_storage_size() == 0


def test_memory_storage_no_disk_writes():
    """Test that files are not written to disk."""
    import os
    
    clear_memory_storage()
    
    # Write to a path that doesn't exist on disk
    test_path = "/nonexistent/directory/test.txt"
    FileIOHelper.write_str("Test content", test_path)
    
    # Verify file was not created on disk
    assert not os.path.exists(test_path)
    
    # Verify data is in memory
    files = get_memory_storage_files()
    assert len(files) > 0


def test_memory_storage_overwrite():
    """Test that overwriting a file in memory works correctly."""
    clear_memory_storage()
    
    # Write initial content
    FileIOHelper.write_str("Initial content", "test/test.txt")
    
    # Overwrite with new content
    FileIOHelper.write_str("Updated content", "test/test.txt")
    
    # Read back
    content = FileIOHelper.read_str("test/test.txt")
    
    assert content == "Updated content"


def test_memory_storage_files_list():
    """Test that get_memory_storage_files returns correct list."""
    clear_memory_storage()
    
    # Write files
    FileIOHelper.write_str("Content 1", "test/file1.txt")
    FileIOHelper.write_str("Content 2", "test/file2.txt")
    
    # Get file list
    files = get_memory_storage_files()
    
    assert len(files) == 2
    assert "test/file1.txt" in files
    assert "test/file2.txt" in files