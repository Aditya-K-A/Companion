import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import settings
from app.llm.gemini import GeminiProvider
from app.prompts.companion import SYSTEM_PROMPT
from app.safety.detector import SafetyDetector, SafetyLevel
from app.memory.manager import MemoryManager

MOOD_OPTIONS = [
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
    "neutral",
]


CRISIS_RESPONSE = """
I'm really sorry you're going through something this painful.

I don't want to pretend that a conversation with me is enough when
someone may be in immediate danger. Please reach out to a trusted person
near you or contact an appropriate local crisis service or emergency
service if you may be in immediate danger.

[CRISIS RESOURCE PLACEHOLDER]

You don't have to handle this completely on your own.
""".strip()


def build_system_prompt(
    relevant_memories: list[str],
    preference: str,
    mood_history: str
):
    memory_text = "\n".join(
        f"- {memory}"
        for memory in relevant_memories
    )

    if not memory_text:
        memory_text = "No relevant long-term memories found."

    return f"""
{SYSTEM_PROMPT}

LONG-TERM MEMORY

The following memories may be relevant to the current conversation.
They are retrieved from previous conversations and may not always be
relevant. Use them only when they naturally apply.

{memory_text}

COMMUNICATION PREFERENCE

{preference}

MOOD HISTORY

The following is a summary of recent emotional patterns.
It is conversational context, not a diagnosis.

{mood_history}

Do not mention the existence of this memory system to the user.
Do not reveal internal memory, preference, or mood-tracking information.
Do not diagnose the user's mental or emotional state.
"""


@st.cache_resource
def initialize_backend():
    llm = GeminiProvider()
    safety = SafetyDetector()
    memory = MemoryManager(llm)

    return llm, safety, memory


def reset_conversation():
    st.session_state.messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]


def main():

    st.set_page_config(
        page_title="Companion",
        page_icon="🌙",
        layout="centered"
    )

    # --------------------------------------------------
    # SESSION STATE
    # --------------------------------------------------

    if "messages" not in st.session_state:
        reset_conversation()

    llm, safety, memory = initialize_backend()

    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------

    st.title("🌙 Companion")

    st.caption(
        "A supportive space to talk, reflect, or simply be heard."
    )

    # --------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------

    with st.sidebar:

        st.header("Companion")

        st.write(
            "Your conversations can be remembered across sessions "
            "to make the companion more context-aware."
        )

        if st.button(
            "Start new conversation",
            use_container_width=True
        ):
            reset_conversation()
            st.rerun()

        st.divider()

        st.subheader("Daily check-in")

        with st.form("daily_mood_checkin"):
            selected_emotion = st.selectbox(
                "How are you feeling today?",
                MOOD_OPTIONS
            )

            intensity_level = st.slider(
                "How strongly are you feeling it?",
                min_value=1,
                max_value=5,
                value=3,
                step=1
            )

            submitted = st.form_submit_button(
                "Save check-in",
                use_container_width=True
            )

            if submitted:
                intensity = intensity_level / 5.0

                memory.database.add_mood_event(
                    user_id=settings.user_id,
                    emotion=selected_emotion,
                    intensity=intensity,
                    confidence=1.0
                )

                st.success("Mood check-in saved.")

        st.caption(
            "This companion is an AI and is not a replacement "
            "for professional or emergency support."
        )

    # --------------------------------------------------
    # DISPLAY CHAT
    # --------------------------------------------------

    for message in st.session_state.messages:

        if message["role"] not in ["user", "assistant"]:
            continue

        avatar = "👤" if message["role"] == "user" else None

        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # --------------------------------------------------
    # INPUT
    # --------------------------------------------------

    user_message = st.chat_input(
        "What's on your mind?"
    )

    if not user_message:
        return

    # Display user message immediately

    with st.chat_message("user", avatar="👤"):
        st.markdown(user_message)

    # --------------------------------------------------
    # SAFETY
    # --------------------------------------------------

    safety_result = safety.detect(user_message)

    if safety_result.level == SafetyLevel.CRISIS:

        response = CRISIS_RESPONSE

        with st.chat_message("assistant"):
            st.markdown(response)

        return

    # --------------------------------------------------
    # MEMORY RETRIEVAL
    # --------------------------------------------------

    context = memory.retrieve_context(
        user_id=settings.user_id,
        query=user_message
    )

    system_prompt = build_system_prompt(
        relevant_memories=context["memories"],
        preference=context["preference"],
        mood_history=context["mood_history"]
    )

    # Replace system prompt with current context

    st.session_state.messages[0] = {
        "role": "system",
        "content": system_prompt
    }

    # Add user message

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    # --------------------------------------------------
    # GENERATE RESPONSE
    # --------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            response = llm.generate(
                st.session_state.messages
            )

        st.markdown(response)

    # Store response

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

    # --------------------------------------------------
    # LONG-TERM MEMORY
    # --------------------------------------------------

    memory.extract_and_store(
        user_id=settings.user_id,
        conversation=st.session_state.messages
    )


if __name__ == "__main__":
    main()