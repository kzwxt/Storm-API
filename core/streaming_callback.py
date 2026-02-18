"""Streaming callback handler for STORM pipeline progress."""

import queue
from typing import Dict, Any, List, Optional
from knowledge_storm.storm_wiki.modules.callback import BaseCallbackHandler


class StreamingCallbackHandler(BaseCallbackHandler):
    """Captures STORM pipeline progress for streaming responses."""

    def __init__(self, topic: Optional[str] = None):
        self.message_queue = queue.Queue()
        self._stage_info: Dict[str, Any] = {
            "perspectives_count": 0,
            "dialogue_turns_count": 0,
            "current_perspective": None,
            "current_query": None,
            "topic": topic
        }

    def clear_progress(self) -> None:
        """Clear all accumulated progress messages."""
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
        """Add a progress message to the queue."""
        self.message_queue.put(message)

    def get_progress(self) -> List[str]:
        """Get all accumulated progress messages."""
        messages = []
        while not self.message_queue.empty():
            try:
                messages.append(self.message_queue.get_nowait())
            except queue.Empty:
                break
        return messages

    def get_message_generator(self):
        """Generator that yields messages as they are added to the queue."""
        while True:
            try:
                message = self.message_queue.get(timeout=0.1)
                yield message
            except queue.Empty:
                break

    def on_identify_perspective_start(self, **kwargs) -> None:
        """Called when STORM starts identifying research perspectives."""
        topic = kwargs.get('topic', self._stage_info.get("topic", "the topic"))
        self.add_progress(f"🔍 Analyzing perspectives for: {topic}")

    def on_identify_perspective_end(self, perspectives: List[str], **kwargs) -> None:
        """Called when STORM finishes identifying perspectives."""
        self._stage_info["perspectives_count"] = len(perspectives)
        self._stage_info["perspectives"] = perspectives

        if perspectives:
            self.add_progress(f"📋 Identified {len(perspectives)} perspectives:")
            for i, perspective in enumerate(perspectives, 1):
                self.add_progress(f"   {i}. {perspective}")
        else:
            self.add_progress("📋 Using general perspective")

    def on_information_gathering_start(self, **kwargs) -> None:
        """Called when STORM starts gathering information for a perspective."""
        perspective = kwargs.get('perspective', self._stage_info.get("current_perspective", "research"))
        self._stage_info["current_perspective"] = perspective
        self.add_progress(f"🔎 Gathering information for: {perspective}")

    def on_information_gathering_end(self, **kwargs) -> None:
        """Called when STORM finishes gathering information."""
        num_queries = kwargs.get('num_queries', 0)
        self.add_progress(f"✓ Gathered information from {num_queries} sources")

    def on_dialogue_turn_end(self, dlg_turn, **kwargs) -> None:
        """Called after each dialogue turn in the research phase."""
        self._stage_info["dialogue_turns_count"] += 1
        turn_num = self._stage_info["dialogue_turns_count"]

        question = None
        for attr in ['conv_q', 'question', 'query']:
            if hasattr(dlg_turn, attr):
                question = getattr(dlg_turn, attr)
                break

        if question is None:
            question = str(dlg_turn)
        elif hasattr(question, 'content'):
            question = question.content

        perspective = kwargs.get('perspective', self._stage_info.get("current_perspective", "research"))
        self._stage_info["current_perspective"] = perspective
        self._stage_info["current_query"] = str(question)

        short_question = str(question)[:80] + "..." if len(str(question)) > 80 else str(question)
        self.add_progress(f"  💬 Q{turn_num}: {short_question}")

    def on_direct_outline_generation_end(self, **kwargs) -> None:
        """Called when STORM generates the direct outline."""
        self.add_progress("📝 Generating article structure (direct outline)")

    def on_outline_refinement_end(self, **kwargs) -> None:
        """Called when STORM refines the outline."""
        self.add_progress("✏️  Refining article structure")

    def on_information_organization_start(self, **kwargs) -> None:
        """Called when STORM starts organizing gathered information."""
        self.add_progress("🗂️  Organizing research information")

    def get_stage_info(self) -> Dict[str, Any]:
        """Get information about the current stage."""
        return self._stage_info.copy()

    def get_summary(self) -> str:
        """Get a summary of all progress."""
        return "\n".join(self.progress_messages)