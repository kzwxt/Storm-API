"""
Streaming Callback Handler Module

This module provides a callback handler for capturing and streaming progress
updates from the STORM pipeline. It enables real-time feedback during article
generation.

Components:
    - StreamingCallbackHandler: Captures STORM progress for streaming responses
"""

import queue
from typing import Dict, Any, List, Optional, Generator

from knowledge_storm.storm_wiki.modules.callback import BaseCallbackHandler


class StreamingCallbackHandler(BaseCallbackHandler):
    """
    Captures STORM pipeline progress for streaming responses.

    This handler extends BaseCallbackHandler to capture progress messages
    from various stages of the STORM pipeline and stores them in a thread-safe
    queue for streaming to clients.

    Attributes:
        message_queue: Thread-safe queue storing progress messages
        _stage_info: Dictionary tracking current pipeline stage information

    Example:
        >>> handler = StreamingCallbackHandler(topic="Python")
        >>> runner.run(topic="Python", callback_handler=handler)
        >>> for message in handler.get_progress():
        ...     print(message)
    """

    def __init__(self, topic: Optional[str] = None) -> None:
        """
        Initialize the streaming callback handler.

        Args:
            topic: Optional topic name for context in progress messages

        Example:
            >>> handler = StreamingCallbackHandler(topic="Python Programming")
        """
        self.message_queue: queue.Queue[str] = queue.Queue()
        self._stage_info: Dict[str, Any] = {
            "perspectives_count": 0,
            "dialogue_turns_count": 0,
            "current_perspective": None,
            "current_query": None,
            "topic": topic
        }

    def clear_progress(self) -> None:
        """
        Clear all accumulated progress messages.

        Resets both the message queue and stage information trackers.

        Example:
            >>> handler.clear_progress()
            >>> # Queue and stage info are now empty
        """
        while not self.message_queue.empty():
            try:
                self.message_queue.get_nowait()
            except queue.Empty:
                break
        self._stage_info = {
            "perspectives_count": 0,
            "dialogue_turns_count": 0,
            "current_perspective": None,
            "current_query": None,
            "topic": self._stage_info.get("topic")
        }

    def add_progress(self, message: str) -> None:
        """
        Add a progress message to the queue.

        Args:
            message: Progress message to add

        Example:
            >>> handler.add_progress("🔍 Starting research...")
        """
        self.message_queue.put(message)

    def get_progress(self) -> List[str]:
        """
        Get all accumulated progress messages.

        Returns:
            List[str]: All progress messages currently in the queue

        Example:
            >>> messages = handler.get_progress()
            >>> for msg in messages:
            ...     print(msg)
        """
        messages: List[str] = []
        while not self.message_queue.empty():
            try:
                messages.append(self.message_queue.get_nowait())
            except queue.Empty:
                break
        return messages

    def get_message_generator(self) -> Generator[str, None, None]:
        """
        Generator that yields messages as they are added to the queue.

        Yields:
            str: Progress messages from the queue

        Example:
            >>> for message in handler.get_message_generator():
            ...     print(message)
        """
        while True:
            try:
                message: str = self.message_queue.get(timeout=0.1)
                yield message
            except queue.Empty:
                break

    def on_identify_perspective_start(self, **kwargs: Any) -> None:
        """
        Called when STORM starts identifying research perspectives.

        Args:
            **kwargs: Additional arguments including 'topic'

        Example:
            >>> # Automatically called by STORM pipeline
            >>> handler.on_identify_perspective_start(topic="Python")
        """
        topic: str = kwargs.get('topic', self._stage_info.get("topic", "the topic"))
        self.add_progress(f"🔍 Analyzing perspectives for: {topic}")

    def on_identify_perspective_end(self, perspectives: List[str], **kwargs: Any) -> None:
        """
        Called when STORM finishes identifying perspectives.

        Args:
            perspectives: List of identified research perspectives
            **kwargs: Additional arguments

        Example:
            >>> # Automatically called by STORM pipeline
            >>> handler.on_identify_perspective_end(perspectives=["History", "Applications"])
        """
        self._stage_info["perspectives_count"] = len(perspectives)
        self._stage_info["perspectives"] = perspectives

        if perspectives:
            self.add_progress(f"📋 Identified {len(perspectives)} perspectives:")
            for i, perspective in enumerate(perspectives, 1):
                self.add_progress(f"   {i}. {perspective}")
        else:
            self.add_progress("📋 Using general perspective")

    def on_information_gathering_start(self, **kwargs: Any) -> None:
        """
        Called when STORM starts gathering information for a perspective.

        Args:
            **kwargs: Additional arguments including 'perspective'

        Example:
            >>> # Automatically called by STORM pipeline
            >>> handler.on_information_gathering_start(perspective="History")
        """
        perspective: str = kwargs.get('perspective', self._stage_info.get("current_perspective", "research"))
        self._stage_info["current_perspective"] = perspective
        self.add_progress(f"🔎 Gathering information for: {perspective}")

    def on_information_gathering_end(self, **kwargs: Any) -> None:
        """
        Called when STORM finishes gathering information.

        Args:
            **kwargs: Additional arguments including 'num_queries'

        Example:
            >>> # Automatically called by STORM pipeline
            >>> handler.on_information_gathering_end(num_queries=5)
        """
        num_queries: int = kwargs.get('num_queries', 0)
        self.add_progress(f"✓ Gathered information from {num_queries} sources")

    def on_dialogue_turn_end(self, dlg_turn: Any, **kwargs: Any) -> None:
        """
        Called after each dialogue turn in the research phase.

        Args:
            dlg_turn: Dialogue turn object containing question/answer
            **kwargs: Additional arguments including 'perspective'

        Example:
            >>> # Automatically called by STORM pipeline
            >>> handler.on_dialogue_turn_end(dlg_turn, perspective="History")
        """
        self._stage_info["dialogue_turns_count"] += 1
        turn_num: int = self._stage_info["dialogue_turns_count"]

        question: Any = None
        for attr in ['conv_q', 'question', 'query']:
            if hasattr(dlg_turn, attr):
                question = getattr(dlg_turn, attr)
                break

        if question is None:
            question = str(dlg_turn)
        elif hasattr(question, 'content'):
            question = question.content

        perspective: str = kwargs.get('perspective', self._stage_info.get("current_perspective", "research"))
        self._stage_info["current_perspective"] = perspective
        self._stage_info["current_query"] = str(question)

        question_str: str = str(question)
        short_question: str = question_str[:80] + "..." if len(question_str) > 80 else question_str
        self.add_progress(f"  💬 Q{turn_num}: {short_question}")

    def on_direct_outline_generation_end(self, **kwargs: Any) -> None:
        """
        Called when STORM generates the direct outline.

        Args:
            **kwargs: Additional arguments

        Example:
            >>> # Automatically called by STORM pipeline
            >>> handler.on_direct_outline_generation_end()
        """
        self.add_progress("📝 Generating article structure (direct outline)")

    def on_outline_refinement_end(self, **kwargs: Any) -> None:
        """
        Called when STORM refines the outline.

        Args:
            **kwargs: Additional arguments

        Example:
            >>> # Automatically called by STORM pipeline
            >>> handler.on_outline_refinement_end()
        """
        self.add_progress("✏️  Refining article structure")

    def on_information_organization_start(self, **kwargs: Any) -> None:
        """
        Called when STORM starts organizing gathered information.

        Args:
            **kwargs: Additional arguments

        Example:
            >>> # Automatically called by STORM pipeline
            >>> handler.on_information_organization_start()
        """
        self.add_progress("🗂️  Organizing research information")

    def get_stage_info(self) -> Dict[str, Any]:
        """
        Get information about the current stage.

        Returns:
            Dict[str, Any]: Copy of current stage information dictionary

        Example:
            >>> info = handler.get_stage_info()
            >>> print(info["perspectives_count"])
        """
        return self._stage_info.copy()

    def get_summary(self) -> str:
        """
        Get a summary of all progress.

        Returns:
            str: Concatenated progress messages

        Example:
            >>> summary = handler.get_summary()
            >>> print(summary)
        """
        return "\n".join(self.progress_messages)