from app.config import settings
from app.llm.gemini import GeminiProvider
from app.prompts.companion import SYSTEM_PROMPT
from app.safety.detector import SafetyDetector, SafetyLevel
from app.memory.manager import MemoryManager



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

def main():

    llm = GeminiProvider()
    safety = SafetyDetector()
    memory = MemoryManager(llm)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    print("Loneliness Support Companion")
    print("Type 'exit' to quit.\n")

    while True:

        user_message = input("You: ").strip()

        if user_message.lower() == "exit":
            break

        if not user_message:
            continue

        # --------------------------------------------------
        # SAFETY
        # --------------------------------------------------

        safety_result = safety.detect(user_message)

        if safety_result.level == SafetyLevel.CRISIS:

            print(
                f"\nCompanion: {CRISIS_RESPONSE}\n"
            )

            continue

        # --------------------------------------------------
        # MEMORY RETRIEVAL
        # --------------------------------------------------

        context = memory.retrieve_context(
            user_id=settings.user_id,
            query=user_message
        )
        # print("\n[DEBUG MOOD]")
        # print(context["mood_history"])
        # print()

        # system_prompt = build_system_prompt(
        #     relevant_memories=context["memories"],
        #     preference=context["preference"]
        # )

        system_prompt = build_system_prompt(
            relevant_memories=context["memories"],
            preference=context["preference"],
            mood_history=context["mood_history"]
        )

        # Replace the previous system prompt
        messages[0] = {
            "role": "system",
            "content": system_prompt
        }

        # --------------------------------------------------
        # CONVERSATION
        # --------------------------------------------------

        messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        response = llm.generate(messages)

        messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        print(
            f"\nCompanion: {response}\n"
        )

        # --------------------------------------------------
        # LONG-TERM MEMORY
        # --------------------------------------------------

        memory.extract_and_store(
            user_id=settings.user_id,
            conversation=messages
        )


if __name__ == "__main__":
    main()