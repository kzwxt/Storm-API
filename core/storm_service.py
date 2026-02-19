"""STORM service wrapper with in-memory storage."""

import os
import queue
import tempfile
import threading
from typing import Dict, Generator, List, Optional

from dotenv import load_dotenv

from knowledge_storm import (
    STORMWikiRunner,
    STORMWikiRunnerArguments,
    STORMWikiLMConfigs,
    DeepSeekModel,
)
from knowledge_storm.rm import SerperRM
from knowledge_storm.utils import FileIOHelper
from core.streaming_callback import StreamingCallbackHandler

_IN_MEMORY_STORAGE: Dict[str, str] = {}

def _normalize_path(file_path: str) -> str:
    """Normalize file path to use forward slashes."""
    return file_path.replace("\\", "/")

def _write_in_memory(s: str, file_path: str) -> None:
    """Store file content in memory."""
    key = _normalize_path(file_path)
    _IN_MEMORY_STORAGE[key] = s

def _read_in_memory(file_path: str) -> str:
    """Read file content from memory."""
    key = _normalize_path(file_path)
    return _IN_MEMORY_STORAGE.get(key, "")

def _exists_in_memory(file_path: str) -> bool:
    """Check if file exists in memory storage."""
    key = _normalize_path(file_path)
    return key in _IN_MEMORY_STORAGE

def _list_files_in_memory(directory: str = "") -> List[str]:
    """
    List all files in memory storage.

    Args:
        directory: Optional directory path to filter files

    Returns:
        List[str]: List of file paths stored in memory

    Example:
        >>> files = _list_files_in_memory("topic")
        >>> print(files)
    """
    prefix: str = _normalize_path(directory)
    if not prefix.endswith("/") and prefix:
        prefix += "/"
    return [key for key in _IN_MEMORY_STORAGE.keys() if key.startswith(prefix)]

def clear_memory_storage() -> None:
    """Clear all in-memory file storage."""
    _IN_MEMORY_STORAGE.clear()

FileIOHelper.write_str = staticmethod(_write_in_memory)
FileIOHelper.read_str = staticmethod(_read_in_memory)

os.environ['PYTHONIOENCODING'] = 'utf-8'
load_dotenv()

DEFAULT_MAX_CONV_TURN = 2
DEFAULT_MAX_PERSPECTIVE = 2
DEFAULT_MAX_SEARCH_QUERIES = 2
DEFAULT_SEARCH_TOP_K = 2
DEFAULT_RETRIEVE_TOP_K = 2
DEFAULT_MAX_THREAD_NUM = 2

class StormService:
    """
    Service wrapper for Stanford STORM with in-memory file storage.
    
    All intermediate files (conversation logs, outlines, articles) are stored
    in RAM without any disk writes. This ensures complete data privacy and
    prevents any information leakage through filesystem.
    
    Orchestrates the complete research-to-article pipeline:
    1. Research: Multi-perspective information gathering
    2. Outline: Structured topic organization
    3. Draft: Article content generation
    4. Polish: Final refinement and summary
    
    All file operations use FileIOHelper overridden with in-memory storage.
    """

    def __init__(self):
        """Initialize STORM service with LLM and retriever configurations"""
        self.lm_configs = self._setup_llm()
        self.retriever = self._setup_retriever()

    # -------------------------------------------------------------------------
    # Configuration Methods
    # -------------------------------------------------------------------------

    def _setup_llm(self) -> STORMWikiLMConfigs:
        """
        Configure DeepSeek language model for all STORM stages.
        
        Returns:
            Configured STORMWikiLMConfigs with DeepSeek model
            
        Raises:
            ValueError: If DEEPSEEK_API_KEY is not set
        """
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY required. Get it at: https://platform.deepseek.com/"
            )

        # Create DeepSeek model instance
        lm = DeepSeekModel(
            model="deepseek-chat",
            api_key=api_key,
            temperature=0.7,
            top_p=0.9
        )

        # Configure all STORM pipeline stages with the same model
        configs = STORMWikiLMConfigs()
        configs.set_conv_simulator_lm(lm)
        configs.set_question_asker_lm(lm)
        configs.set_outline_gen_lm(lm)
        configs.set_article_gen_lm(lm)
        configs.set_article_polish_lm(lm)

        return configs

    def _setup_retriever(self) -> SerperRM:
        """
        Configure Serper search retriever.
        
        Returns:
            Configured SerperRM instance
            
        Raises:
            ValueError: If SERPER_API_KEY is not set
        """
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            raise ValueError(
                "SERPER_API_KEY required. Get free key at: https://serper.dev/"
            )

        return SerperRM(
            serper_search_api_key=api_key,
            k=self._get_int_env("SEARCH_TOP_K", DEFAULT_SEARCH_TOP_K)
        )

    def _get_int_env(self, key: str, default: int) -> int:
        """Helper to safely get integer from environment variables"""
        try:
            return int(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            return default

    def _get_bool_env(self, key: str, default: bool = True) -> bool:
        """Helper to safely get boolean from environment variables"""
        return os.getenv(key, str(default)).lower() == "true"

    # -------------------------------------------------------------------------
    # Pipeline Execution
    # -------------------------------------------------------------------------

    def run(self, topic: str) -> str:
        """
        Execute the complete STORM pipeline for a given topic.

        All file operations are performed in-memory without touching the disk.

        Args:
            topic: Research topic to generate article about

        Returns:
            Generated article text in Markdown format

        Raises:
            Exception: If pipeline execution fails
        """
        # Clear any previous in-memory storage
        clear_memory_storage()

        try:
            # Step 1: Configure pipeline parameters
            # Use temporary directory path - files won't be written to disk
            import tempfile
            temp_dir = tempfile.mkdtemp()
            args = self._build_runner_args(temp_dir)

            # Step 2: Create STORM runner
            runner = STORMWikiRunner(
                args=args,
                lm_configs=self.lm_configs,
                rm=self.retriever
            )

            # Step 3: Determine which stages to run
            pipeline_config = self._get_pipeline_config()

            # Step 4: Execute STORM pipeline (all files stored in memory)
            runner.run(topic=topic, **pipeline_config)

            # Step 5: Retrieve article from memory and return
            return self._get_article_from_memory(pipeline_config)

        except AssertionError as e:
            raise self._format_error("Assertion error", str(e))
        except Exception as e:
            error_msg = str(e)
            if "RatelimitException" in type(e).__name__:
                raise Exception("Search rate limit exceeded. Try again in a few moments.")
            raise self._format_error("Pipeline execution failed", error_msg)

    def run_with_streaming(self, topic: str, callback_handler: Optional[StreamingCallbackHandler] = None) -> Generator[str, None, None]:
        """
        Execute STORM pipeline with streaming progress updates.

        This method yields progress messages at each stage of the STORM pipeline
        using the callback handler, providing real-time feedback to the user.

        Args:
            topic: Research topic to generate article about
            callback_handler: Optional callback handler for streaming progress

        Yields:
            str: Progress messages and the final article

        Raises:
            Exception: If pipeline execution fails
        """
        # Clear any previous in-memory storage
        clear_memory_storage()

        # Create callback handler if not provided
        if callback_handler is None:
            callback_handler = StreamingCallbackHandler(topic=topic)

        callback_handler.clear_progress()

        # Result storage to get the article after STORM completes
        result_container = {"article": None, "error": None, "config": None}

        try:
            # Yield initial message
            yield f"🔍 Starting research on: {topic}\n\n"

            # Configure pipeline parameters
            args = self._build_runner_args("/dev/null")

            # Create STORM runner
            runner = STORMWikiRunner(
                args=args,
                lm_configs=self.lm_configs,
                rm=self.retriever
            )

            # Determine which stages to run
            pipeline_config = self._get_pipeline_config()
            result_container["config"] = pipeline_config

            # Function to run STORM in a separate thread
            def run_storm():
                try:
                    # Execute STORM pipeline with callback handler
                    runner.run(topic=topic, callback_handler=callback_handler, **pipeline_config)
                    # Retrieve article and store it
                    result_container["article"] = self._get_article_from_memory(pipeline_config)
                except Exception as e:
                    result_container["error"] = e

            # Start STORM in a background thread
            storm_thread = threading.Thread(target=run_storm, daemon=True)
            storm_thread.start()

            # Yield messages as they arrive from the callback handler
            while storm_thread.is_alive():
                try:
                    # Get any new messages from the queue
                    message = callback_handler.message_queue.get(timeout=0.1)
                    yield f"{message}\n"
                except queue.Empty:
                    # No new messages, continue checking
                    continue

            # Wait for thread to complete and get any remaining messages
            storm_thread.join(timeout=5)

            # Yield any remaining messages
            while not callback_handler.message_queue.empty():
                try:
                    message = callback_handler.message_queue.get_nowait()
                    yield f"{message}\n"
                except queue.Empty:
                    break

            # Check for errors
            if result_container["error"]:
                error_msg = str(result_container["error"])
                if "RatelimitException" in type(result_container["error"]).__name__:
                    yield "❌ Search rate limit exceeded. Try again in a few moments.\n"
                    raise Exception("Search rate limit exceeded. Try again in a few moments.")
                yield f"❌ Pipeline execution failed: {error_msg}\n"
                raise self._format_error("Pipeline execution failed", error_msg)

            # Yield stage completion messages
            yield "\n"

            if pipeline_config.get("do_research"):
                yield "✅ Research phase complete\n\n"

            if pipeline_config.get("do_generate_outline"):
                yield "📝 Outline generated\n\n"

            if pipeline_config.get("do_generate_article"):
                yield "✍️  Article generated\n\n"

            if pipeline_config.get("do_polish_article"):
                yield "✨ Article polished\n\n"

            yield "📄 Final Article:\n"
            yield "────────────────────────────────────────\n\n"

            # Yield final article
            yield result_container["article"]

        except AssertionError as e:
            yield f"❌ Assertion error: {str(e)}\n"
            raise self._format_error("Assertion error", str(e))
        except Exception as e:
            error_msg = str(e)
            if "RatelimitException" in type(e).__name__:
                yield "❌ Search rate limit exceeded. Try again in a few moments.\n"
                raise Exception("Search rate limit exceeded. Try again in a few moments.")
            yield f"❌ Pipeline execution failed: {error_msg}\n"
            raise self._format_error("Pipeline execution failed", error_msg)
        """
        Execute the complete STORM pipeline for a given topic.
        
        All file operations are performed in-memory without touching the disk.
        
        Args:
            topic: Research topic to generate article about
            
        Returns:
            Generated article text in Markdown format
            
        Raises:
            Exception: If pipeline execution fails
        """
        # Clear any previous in-memory storage
        clear_memory_storage()
        
        try:
            # Step 1: Configure pipeline parameters
            # Use dummy path - files won't be written to disk
            args = self._build_runner_args("/dev/null")
            
            # Step 2: Create STORM runner
            runner = STORMWikiRunner(
                args=args,
                lm_configs=self.lm_configs,
                rm=self.retriever
            )
            
            # Step 3: Determine which stages to run
            pipeline_config = self._get_pipeline_config()
            
            # Step 4: Execute STORM pipeline (all files stored in memory)
            runner.run(topic=topic, **pipeline_config)
            
            # Step 5: Retrieve article from memory and return
            return self._get_article_from_memory(pipeline_config)
                
        except AssertionError as e:
            raise self._format_error("Assertion error", str(e))
        except Exception as e:
            error_msg = str(e)
            if "RatelimitException" in type(e).__name__:
                raise Exception("Search rate limit exceeded. Try again in a few moments.")
            raise self._format_error("Pipeline execution failed", error_msg)

    def _build_runner_args(self, output_dir: str) -> STORMWikiRunnerArguments:
        """Build STORM runner arguments from environment configuration"""
        return STORMWikiRunnerArguments(
            output_dir=output_dir,
            max_conv_turn=self._get_int_env("MAX_CONV_TURN", DEFAULT_MAX_CONV_TURN),
            max_perspective=self._get_int_env("MAX_PERSPECTIVE", DEFAULT_MAX_PERSPECTIVE),
            max_search_queries_per_turn=self._get_int_env(
                "MAX_SEARCH_QUERIES_PER_TURN", 
                DEFAULT_MAX_SEARCH_QUERIES
            ),
            disable_perspective=not self._get_bool_env("ENABLE_PERSPECTIVE", True),
            search_top_k=self._get_int_env("SEARCH_TOP_K", DEFAULT_SEARCH_TOP_K),
            retrieve_top_k=self._get_int_env("RETRIEVE_TOP_K", DEFAULT_RETRIEVE_TOP_K),
            max_thread_num=self._get_int_env("MAX_THREAD_NUM", DEFAULT_MAX_THREAD_NUM)
        )

    def _get_pipeline_config(self) -> Dict[str, bool]:
        """
        Get pipeline stage configuration.

        Returns:
            Dict[str, bool]: Dictionary mapping stage names to boolean flags

        Example:
            >>> config = self._get_pipeline_config()
            >>> print(config["do_research"])
        """
        return {
            "do_research": self._get_bool_env("DO_RESEARCH", True),
            "do_generate_outline": self._get_bool_env("DO_GENERATE_OUTLINE", True),
            "do_generate_article": self._get_bool_env("DO_GENERATE_ARTICLE", True),
            "do_polish_article": self._get_bool_env("DO_POLISH_ARTICLE", True),
        }

    # -------------------------------------------------------------------------
    # In-Memory File Retrieval
    # -------------------------------------------------------------------------

    def _get_article_from_memory(self, config: dict) -> str:
        """
        Retrieve the generated article from in-memory storage.
        
        STORM stores articles with paths like:
            /dev/null/TopicName/polished_article.txt
            /dev/null/TopicName/storm_gen_article.txt
        
        Args:
            config: Pipeline configuration (to check if polishing was enabled)
            
        Returns:
            Article text content
            
        Raises:
            Exception: If no article file is found in memory
        """
        # List all files in memory storage
        all_files = _list_files_in_memory()
        
        if not all_files:
            raise Exception("No files were generated in memory storage")
        
        # Try to find polished article first
        if config.get("do_polish_article"):
            polished_files = [f for f in all_files if "polished_article.txt" in f]
            if polished_files:
                return _IN_MEMORY_STORAGE[polished_files[0]]
        
        # Fallback to draft article
        draft_files = [f for f in all_files if "storm_gen_article.txt" in f]
        if draft_files:
            return _IN_MEMORY_STORAGE[draft_files[0]]
        
        # No article found
        raise Exception(f"No article file found in memory. Available files: {all_files}")

    # -------------------------------------------------------------------------
    # Error Handling
    # -------------------------------------------------------------------------

    def _format_error(self, error_type: str, message: str) -> Exception:
        """
        Format error with traceback for debugging.

        Args:
            error_type: Type/category of the error
            message: Error message description

        Returns:
            Exception: Formatted exception with traceback

        Example:
            >>> error = self._format_error("Validation", "Invalid input")
            >>> raise error
        """
        import traceback
        full_message: str = f"STORM {error_type}: {message}\nTraceback: {traceback.format_exc()}"
        return Exception(full_message)


# ==============================================================================
# Public Utility Functions
# ==============================================================================

def get_memory_storage_size() -> int:
    """
    Get the current size of in-memory storage.
    
    Returns:
        Number of files currently stored in memory
        
    Example:
        >>> from core.storm_service import get_memory_storage_size
        >>> print(f"Files in memory: {get_memory_storage_size()}")
    """
    return len(_IN_MEMORY_STORAGE)


def get_memory_storage_files() -> List[str]:
    """
    Get list of all files currently in memory storage.

    Returns:
        List[str]: List of file paths stored in memory

    Example:
        >>> from core.storm_service import get_memory_storage_files
        >>> files = get_memory_storage_files()
        >>> for f in files:
        ...     print(f)
    """
    return list(_IN_MEMORY_STORAGE.keys())