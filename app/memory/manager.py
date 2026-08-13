import json
import uuid

from app.config import settings
from app.memory.database import Database
from app.memory.long_term import LongTermMemory
from app.prompts.memory import MEMORY_EXTRACTION_PROMPT




class MemoryManager:

    def __init__(self, llm):
        self.llm = llm
        self.database = Database()
        self.long_term = LongTermMemory()

    # --------------------------------------------------
    # LONG-TERM MEMORY + MOOD EXTRACTION
    # --------------------------------------------------

    def extract_and_store(
        self,
        user_id: str,
        conversation: list[dict]
    ):

        recent_conversation = conversation[
            -settings.conversation_window:
        ]

        conversation_text = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in recent_conversation
        )

        messages = [
            {
                "role": "system",
                "content": MEMORY_EXTRACTION_PROMPT
            },
            {
                "role": "user",
                "content": conversation_text
            }
        ]

        raw_result = self.llm.generate(messages)

        try:
            result = json.loads(raw_result)
        except json.JSONDecodeError:
            return

        # --------------------------------------------------
        # MEMORIES
        # --------------------------------------------------

        memories = result.get("memories", [])

        for memory in memories:

            content = memory.get("content")
            memory_type = memory.get(
                "type",
                "general"
            )
            confidence = memory.get(
                "confidence",
                0.5
            )

            if not content:
                continue

            memory_id = str(uuid.uuid4())

            stored = self.database.add_memory(
                user_id=user_id,
                memory_type=memory_type,
                content=content,
                confidence=confidence
            )

            if stored:
                self.long_term.add_memory(
                    user_id=user_id,
                    memory_id=memory_id,
                    content=content
                )

        # --------------------------------------------------
        # COMMUNICATION PREFERENCE
        # --------------------------------------------------

        preference = result.get(
            "preference_signal",
            {}
        )

        self.database.update_preference(
            user_id=user_id,
            advice_delta=preference.get(
                "advice",
                0
            ),
            venting_delta=preference.get(
                "venting",
                0
            )
        )

        # --------------------------------------------------
        # MOOD
        # --------------------------------------------------

        mood = result.get(
            "mood_signal",
            {}
        )

        emotion = mood.get(
            "emotion",
            "neutral"
        )

        intensity = mood.get(
            "intensity",
            0.0
        )

        confidence = mood.get(
            "confidence",
            0.0
        )

        valid_emotions = {
            "lonely",
            "sad",
            "anxious",
            "frustrated",
            "angry",
            "overwhelmed",
            "hopeless",
            "hopeful",
            "happy",
            "calm",
            "neutral"
        }

        if emotion not in valid_emotions:
            emotion = "neutral"

        try:
            intensity = float(intensity)
            confidence = float(confidence)
        except (TypeError, ValueError):
            intensity = 0.0
            confidence = 0.0

        intensity = max(
            0.0,
            min(1.0, intensity)
        )

        confidence = max(
            0.0,
            min(1.0, confidence)
        )

        # Don't store an uncertain neutral signal.
        if not (
            emotion == "neutral"
            and confidence == 0.0
        ):
            self.database.add_mood_event(
                user_id=user_id,
                emotion=emotion,
                intensity=intensity,
                confidence=confidence
            )

    # --------------------------------------------------
    # CONTEXT RETRIEVAL
    # --------------------------------------------------

    def retrieve_context(
        self,
        user_id: str,
        query: str
    ):

        memories = self.long_term.retrieve(
            user_id=user_id,
            query=query,
            top_k=settings.memory_retrieval_top_k
        )

        # --------------------------------------------------
        # COMMUNICATION PREFERENCE
        # --------------------------------------------------

        preference = self.database.get_preference(
            user_id
        )

        if preference:

            advice_score, venting_score = preference

            if advice_score > venting_score:

                preference_text = (
                    "The user generally responds well to "
                    "practical advice when discussing problems."
                )

            elif venting_score > advice_score:

                preference_text = (
                    "The user generally prefers emotional "
                    "listening over unsolicited advice."
                )

            else:

                preference_text = (
                    "There is not enough evidence to determine "
                    "whether the user prefers advice or venting."
                )

        else:

            preference_text = (
                "There is not enough evidence to determine "
                "whether the user prefers advice or venting."
            )

        # --------------------------------------------------
        # MOOD HISTORY
        # --------------------------------------------------

        recent_moods = self.database.get_recent_moods(
            user_id=user_id,
            limit=settings.mood_history_limit
        )

        mood_history = self._build_mood_summary(
            recent_moods
        )

        return {
            "memories": memories,
            "preference": preference_text,
            "mood_history": mood_history
        }

    # --------------------------------------------------
    # MOOD SUMMARY
    # --------------------------------------------------

    def _build_mood_summary(self, mood_events):

        if not mood_events:
            return "No recent mood history is available."

        # mood_events are ordered newest -> oldest
        latest = mood_events[0]

        latest_emotion = latest[0]
        latest_intensity = float(latest[1])

        previous_emotion = None

        if len(mood_events) > 1:
            previous_emotion = mood_events[1][0]

        # --------------------------------------------------
        # Emotion frequency
        # --------------------------------------------------

        emotion_counts = {}

        for event in mood_events:
            emotion = event[0]

            emotion_counts[emotion] = (
                emotion_counts.get(emotion, 0) + 1
            )

        dominant_emotion = max(
            emotion_counts,
            key=emotion_counts.get
        )

        # Only call something "recurring" if it appears more than once.
        recurring_emotions = [
            emotion
            for emotion, count in emotion_counts.items()
            if count > 1
        ]

        # --------------------------------------------------
        # Average intensity
        # --------------------------------------------------

        intensities = [
            float(event[1])
            for event in mood_events
        ]

        average_intensity = (
            sum(intensities) / len(intensities)
        )

        if average_intensity >= 0.75:
            intensity_description = "high"
        elif average_intensity >= 0.45:
            intensity_description = "moderate"
        else:
            intensity_description = "low"

        # --------------------------------------------------
        # Pattern
        # --------------------------------------------------

        unique_emotions = {
            event[0]
            for event in mood_events
        }

        if len(unique_emotions) == 1:
            pattern = "consistent"

        elif len(unique_emotions) >= 3:
            pattern = "mixed"

        else:
            pattern = "some variation"

        # --------------------------------------------------
        # Build context
        # --------------------------------------------------

        summary_parts = []

        summary_parts.append(
            f"Latest observed mood: {latest_emotion} "
            f"(intensity {latest_intensity:.2f})."
        )

        if previous_emotion:
            summary_parts.append(
                f"Previous observed mood: {previous_emotion}."
            )

        if recurring_emotions:
            summary_parts.append(
                "Recurring recent emotions: "
                + ", ".join(recurring_emotions)
                + "."
            )

        summary_parts.append(
            f"Overall recent pattern: {pattern}."
        )

        summary_parts.append(
            f"Average recent emotional intensity: "
            f"{intensity_description}."
        )

        return " ".join(summary_parts)